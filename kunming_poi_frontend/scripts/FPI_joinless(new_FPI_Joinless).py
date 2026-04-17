# __*__ coding=utf-8 __*__
# @author Hackerdallas
# Joinless 算法实现：空间同位模式 FPI 挖掘（大数据集适配版 — 磁盘索引 + 多进程并行计算）
import pandas as pd
import BasicToos2025070
import itertools
import time
import gc
import psutil
import os
import matplotlib.pyplot as plt
import pickle
import shelve
import dbm
from multiprocessing import Pool, cpu_count
from functools import partial

# ==================== 性能调控参数 ====================
# 每种事件类型参与笛卡尔积的最大邻居数（按隶属度降序截断）
# 设为 None 表示不截断，完全精确计算
MAX_NEI_PER_EVENT = 8
# 模式扩展的最大阶数（2阶→3阶→...→MAX_LEVEL阶）
# 设为 None 表示不限制
MAX_LEVEL = 4
# 多进程并行核心数（设为 None 则自动检测 CPU 核心数）
NUM_PROCESSES = None
# =======================================================

# 获取候选模式
def genCandidatePatterns(priorPatterns_f_gcp):
    candidatePatterns_f_gcp = []
    priorPatterns_f_gcp = sorted(priorPatterns_f_gcp)
    for loop_pattern_f_gcp in priorPatterns_f_gcp:
        curLoopPatternIndex_f_gcp = priorPatterns_f_gcp.index(loop_pattern_f_gcp)
        for innerLoop_pattern_f_gcp in priorPatterns_f_gcp[curLoopPatternIndex_f_gcp + 1:]:
            if (loop_pattern_f_gcp[0:len(loop_pattern_f_gcp) - 1] == innerLoop_pattern_f_gcp[
                                                                     0:len(loop_pattern_f_gcp) - 1]):
                candidatePatterns_f_gcp.append(loop_pattern_f_gcp + innerLoop_pattern_f_gcp[-1])
            else:
                break
    return candidatePatterns_f_gcp


# ==================== 磁盘索引：将碎片文件合并为 shelve 数据库 ====================
# 索引结构: shelve_db[str(centerIndex)] = {neiIndex: memValue, ...}
# 这样查询某个中心点的所有邻居隶属度只需一次磁盘读取

SHELVE_DB_PATH = "./mem_value_index"
NEI_INDEX_DB_PATH = "./nei_index"

def build_shelve_index(chunk_files, force_rebuild=False):
    """将所有碎片 pkl 文件合并为一个 shelve 磁盘数据库，返回 shelve 句柄"""
    # 检查是否已存在索引（shelve 在不同平台可能产生 .db / .dir+.bak+.dat 等后缀）
    if not force_rebuild:
        # 尝试打开已有索引
        try:
            db = shelve.open(SHELVE_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL)
            if len(db) > 0:
                print(f"[+] 检测到已有磁盘索引 ({SHELVE_DB_PATH})，包含 {len(db)} 个中心点，跳过重建", flush=True)
                db.close()
                db = shelve.open(SHELVE_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL)
                return db
            db.close()
        except Exception:
            pass

    print(f"[*] 正在从 {len(chunk_files)} 个碎片文件构建磁盘索引 ({SHELVE_DB_PATH})...", flush=True)
    # 使用临时内存字典分批累积后写入 shelve，减少小步写入的开销
    mem_buffer = {}
    BUFFER_FLUSH_SIZE = 10000  # 减小缓冲区大小，更频繁释放内存

    db = shelve.open(SHELVE_DB_PATH, flag='n', protocol=pickle.HIGHEST_PROTOCOL, writeback=False)

    for file_idx, file in enumerate(chunk_files):
        try:
            with open(file, 'rb') as f:
                local_pairs, _ = pickle.load(f)
            for pat, pairs_dict in local_pairs.items():
                for (cur, comp), memVal in pairs_dict.items():
                    cur_str = str(cur)
                    if cur_str not in mem_buffer:
                        mem_buffer[cur_str] = {}
                    mem_buffer[cur_str][comp] = memVal
            del local_pairs
        except Exception as e:
            pass

        # 定期将缓冲区刷入 shelve
        if len(mem_buffer) >= BUFFER_FLUSH_SIZE or file_idx == len(chunk_files) - 1:
            for k, v in mem_buffer.items():
                if k in db:
                    existing = db[k]
                    existing.update(v)
                    db[k] = existing
                else:
                    db[k] = v
            db.sync()  # 强制同步到磁盘
            mem = psutil.virtual_memory()
            print(f"   -> 索引构建进度: {file_idx+1}/{len(chunk_files)} 文件, 已写入 {len(db)} 个中心点 | 内存: {mem.percent}%", flush=True)
            mem_buffer.clear()
            gc.collect()

    db.sync()
    print(f"[+] 磁盘索引构建完成，共 {len(db)} 个中心点", flush=True)
    # 关闭后以只读模式重新打开
    db.close()
    db = shelve.open(SHELVE_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL, writeback=False)
    return db


def shelve_get_mem_value(db, centerIndex, neiIndex):
    """从 shelve 索引中查询两个实例之间的隶属度"""
    key = str(centerIndex)
    if key not in db:
        return None
    nei_map = db[key]
    return nei_map.get(neiIndex, None)


def shelve_get_nei_map(db, centerIndex):
    """从 shelve 索引中获取某个中心点的全部邻居隶属度字典"""
    key = str(centerIndex)
    if key not in db:
        return {}
    return db[key]


# ==================== 计算模式的紧密度（基于 shelve 磁盘索引） ====================
def getCompactValue(rowInstance, mem_db):
    """计算一个行实例的紧密度，mem_db 为 shelve 句柄"""
    cliqueFlag = True
    compactValueList = []
    level = len(rowInstance)
    # 预加载本行实例涉及的所有中心点的邻居映射（LRU 式批量读取，减少磁盘访问次数）
    local_cache = {}
    for idx in range(level):
        inst = rowInstance[idx]
        if inst not in local_cache:
            local_cache[inst] = shelve_get_nei_map(mem_db, inst)

    outInstanceIndex = 0
    while (outInstanceIndex < level):
        curInstanceIndex = rowInstance[outInstanceIndex]
        compactValue = 1.0
        inInstanceIndex = 0
        while (inInstanceIndex < level):
            comparedInstanceIndex = rowInstance[inInstanceIndex]
            if (outInstanceIndex < inInstanceIndex):
                neiMap = local_cache.get(curInstanceIndex, {})
                if comparedInstanceIndex not in neiMap:
                    cliqueFlag = False
                    break
                compactValue = min(compactValue, neiMap[comparedInstanceIndex])
            elif (outInstanceIndex > inInstanceIndex):
                neiMap = local_cache.get(comparedInstanceIndex, {})
                if curInstanceIndex not in neiMap:
                    cliqueFlag = False
                    break
                compactValue = min(compactValue, neiMap[curInstanceIndex])
            inInstanceIndex += 1
        if(cliqueFlag == False):
            break
        compactValueList.append(compactValue)
        outInstanceIndex += 1
    return cliqueFlag, compactValueList


# ==================== 多进程工作函数（子进程执行） ====================
def process_center_chunk(args):
    """
    多进程工作函数：处理一批中心点
    每个子进程独立打开 shelve 数据库，处理分配的中心点列表
    """
    center_keys, candidatePatterns_f, fpiThreshold_local, eventCount_local, idInstanceMap_local = args
    
    # 子进程独立打开只读 shelve 数据库
    mem_db = shelve.open(SHELVE_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL, writeback=False)
    nei_db = shelve.open(NEI_INDEX_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL, writeback=False)
    
    pattern_event_compact = {}
    star_instance_count = 0
    
    for centerIndex in center_keys:
        centerIndexInt = int(centerIndex) if isinstance(centerIndex, str) else centerIndex
        
        if centerIndex not in nei_db:
            continue
        comps = nei_db[centerIndex]
        centerEvent = idInstanceMap_local[centerIndexInt][1]
        
        # 动态构建 rawNeiMap
        rawNeiMap = {}
        for comp in comps:
            compEvent = idInstanceMap_local[comp][1]
            if compEvent not in rawNeiMap:
                rawNeiMap[compEvent] = []
            rawNeiMap[compEvent].append(comp)
        
        # 截断邻居
        center_nei_mem = shelve_get_nei_map(mem_db, centerIndexInt)
        truncatedNeiMap = {}
        for ev, nList in rawNeiMap.items():
            if MAX_NEI_PER_EVENT is not None and len(nList) > MAX_NEI_PER_EVENT:
                truncatedNeiMap[ev] = sorted(nList,
                    key=lambda x: center_nei_mem.get(x, 0),
                    reverse=True)[:MAX_NEI_PER_EVENT]
            else:
                truncatedNeiMap[ev] = nList
        truncatedNeiMap[centerEvent] = [centerIndexInt]
        
        eventSet = set(truncatedNeiMap.keys())
        
        for candidatePattern in candidatePatterns_f:
            if candidatePattern[0] != centerEvent:
                continue
            if not all(e in eventSet for e in candidatePattern):
                continue
            
            instanceListList = []
            skip = False
            for event in candidatePattern:
                if event not in truncatedNeiMap:
                    skip = True
                    break
                instanceListList.append(truncatedNeiMap[event])
            if skip or len(instanceListList) == 0:
                continue
            
            if candidatePattern not in pattern_event_compact:
                pattern_event_compact[candidatePattern] = {}
            
            # 流式处理笛卡尔积
            for starInstance in itertools.product(*instanceListList):
                star_instance_count += 1
                
                cliqueFlag, compactValueList = getCompactValue(starInstance, mem_db)
                if not cliqueFlag:
                    continue
                
                ecMap = pattern_event_compact[candidatePattern]
                level = len(candidatePattern)
                for idx in range(level):
                    eventKey = candidatePattern[idx]
                    instanceCompact = ecMap.get(eventKey, {})
                    oldVal = instanceCompact.get(starInstance[idx], 0)
                    instanceCompact[starInstance[idx]] = max(oldVal, compactValueList[idx])
                    ecMap[eventKey] = instanceCompact
        
        del rawNeiMap, truncatedNeiMap, center_nei_mem, eventSet
    
    # 关闭子进程的数据库连接
    mem_db.close()
    nei_db.close()
    
    return pattern_event_compact, star_instance_count


# ==================== 单进程流式计算（基于磁盘索引，内存安全） ====================
def getFreqPatternsStreaming(candidatePatterns_f, centerIndexEventNeiIndexMap_f, mem_db):
    """
    单进程流式计算频繁模式的紧密度。
    mem_db: shelve 磁盘索引句柄，按需读取隶属度，不占用大量内存。
    """
    pattern_event_compact = {}
    total_centers = len(centerIndexEventNeiIndexMap_f)
    processed = 0
    star_instance_count = 0
    
    # 内存监控阈值：当内存使用超过85%时触发强制GC
    MEMORY_THRESHOLD = 85

    for centerIndex in centerIndexEventNeiIndexMap_f:
        processed += 1
        
        # 定期内存监控和清理
        if processed % 1000 == 0:
            mem = psutil.virtual_memory()
            if mem.percent > MEMORY_THRESHOLD:
                print(f"   [Streaming] 内存告警: {mem.percent}% | 强制GC清理", flush=True)
                gc.collect()
            
            if processed % 5000 == 0:
                print(f"   [Streaming] 进度: {processed}/{total_centers} ({processed/total_centers*100:.1f}%) | 内存: {mem.percent}% | 累计实例: {star_instance_count}", flush=True)

        # shelve 键为字符串，需转换为整数以访问 idInstanceMap
        centerIndexInt = int(centerIndex) if isinstance(centerIndex, str) else centerIndex
        comps = centerIndexEventNeiIndexMap_f[centerIndex]
        centerEvent = idInstanceMap[centerIndexInt][1]

        # 动态构建 rawNeiMap
        rawNeiMap = {}
        for comp in comps:
            compEvent = idInstanceMap[comp][1]
            if compEvent not in rawNeiMap:
                rawNeiMap[compEvent] = []
            rawNeiMap[compEvent].append(comp)

        # 一次性截断：对当前中心的所有事件邻居执行截断排序
        # 从磁盘索引中读取当前中心点的邻居隶属度（仅一次磁盘读取）
        center_nei_mem = shelve_get_nei_map(mem_db, centerIndexInt)
        truncatedNeiMap = {}
        for ev, nList in rawNeiMap.items():
            if MAX_NEI_PER_EVENT is not None and len(nList) > MAX_NEI_PER_EVENT:
                truncatedNeiMap[ev] = sorted(nList,
                    key=lambda x: center_nei_mem.get(x, 0),
                    reverse=True)[:MAX_NEI_PER_EVENT]
            else:
                truncatedNeiMap[ev] = nList
        truncatedNeiMap[centerEvent] = [centerIndexInt]

        eventSet = set(truncatedNeiMap.keys())

        for candidatePattern in candidatePatterns_f:
            if candidatePattern[0] != centerEvent:
                continue
            if not all(e in eventSet for e in candidatePattern):
                continue

            instanceListList = []
            skip = False
            for event in candidatePattern:
                if event not in truncatedNeiMap:
                    skip = True
                    break
                instanceListList.append(truncatedNeiMap[event])
            if skip or len(instanceListList) == 0:
                continue

            if candidatePattern not in pattern_event_compact:
                pattern_event_compact[candidatePattern] = {}

            # 流式处理笛卡尔积
            for starInstance in itertools.product(*instanceListList):
                star_instance_count += 1

                cliqueFlag, compactValueList = getCompactValue(starInstance, mem_db)
                if not cliqueFlag:
                    continue

                ecMap = pattern_event_compact[candidatePattern]
                level = len(candidatePattern)
                for idx in range(level):
                    eventKey = candidatePattern[idx]
                    instanceCompact = ecMap.get(eventKey, {})
                    oldVal = instanceCompact.get(starInstance[idx], 0)
                    instanceCompact[starInstance[idx]] = max(oldVal, compactValueList[idx])
                    ecMap[eventKey] = instanceCompact
        
        # 释放临时变量
        del rawNeiMap, truncatedNeiMap, center_nei_mem, eventSet

    print(f"   [Streaming] 完成，处理 {len(pattern_event_compact)} 个模式，累计 {star_instance_count} 个星型实例", flush=True)
    return pattern_event_compact, star_instance_count


# ==================== 多进程并行计算入口 ====================
def getFreqPatternsMultiProcess(candidatePatterns_f, centerIndexEventNeiIndexMap_f, fpiThreshold_local, eventCount_local, idInstanceMap_local):
    """
    多进程并行计算频繁模式
    将中心点列表分片，每个进程处理一部分，最后合并结果
    """
    # 确定进程数
    num_processes = NUM_PROCESSES if NUM_PROCESSES is not None else cpu_count()
    num_processes = min(num_processes, len(centerIndexEventNeiIndexMap_f))  # 不超过中心点数量
    
    print(f"   [多进程] 使用 {num_processes} 个进程并行计算", flush=True)
    
    # 将中心点列表分片
    center_keys = list(centerIndexEventNeiIndexMap_f.keys())
    chunk_size = (len(center_keys) + num_processes - 1) // num_processes
    center_chunks = [center_keys[i:i+chunk_size] for i in range(0, len(center_keys), chunk_size)]
    
    print(f"   [多进程] 将 {len(center_keys)} 个中心点分为 {len(center_chunks)} 个任务块", flush=True)
    
    # 准备多进程参数
    args_list = [
        (chunk, candidatePatterns_f, fpiThreshold_local, eventCount_local, idInstanceMap_local)
        for chunk in center_chunks
    ]
    
    # 启动多进程池
    start_time = time.time()
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_center_chunk, args_list)
    
    elapsed = time.time() - start_time
    print(f"   [多进程] 并行计算完成，耗时 {elapsed:.2f} 秒", flush=True)
    
    # 合并所有进程的结果
    print(f"   [多进程] 正在合并 {len(results)} 个进程的结果...", flush=True)
    merged_pattern_event_compact = {}
    total_star_count = 0
    
    for pattern_event_compact, star_count in results:
        total_star_count += star_count
        for pattern, ecMap in pattern_event_compact.items():
            if pattern not in merged_pattern_event_compact:
                merged_pattern_event_compact[pattern] = {}
            
            for event, instanceCompact in ecMap.items():
                if event not in merged_pattern_event_compact[pattern]:
                    merged_pattern_event_compact[pattern][event] = {}
                
                # 合并实例紧密度（取最大值）
                for inst, compact_val in instanceCompact.items():
                    old_val = merged_pattern_event_compact[pattern][event].get(inst, 0)
                    merged_pattern_event_compact[pattern][event][inst] = max(old_val, compact_val)
    
    print(f"   [多进程] 合并完成，累计处理 {total_star_count} 个星型实例", flush=True)
    
    return merged_pattern_event_compact, total_star_count


# ==================== 统一入口：多进程并行 + 批处理 ====================
def getFreqPatterns(candidatePatterns_f, centerIndexEventNeiIndexMap_f, mem_db):
    """
    mem_db: shelve 磁盘索引句柄（替代原来的 chunk_files 列表）
    """
    pattern_Fpi = {}

    # 设定调度批处理维度，控制 pattern_event_compact 字典结构占用内存极限
    batch_size = 10
    total_candidates = len(candidatePatterns_f)
    print(f"   [批处理] 将候选模式划分为 {((total_candidates - 1) // batch_size) + 1} 个批次, 每批大小: {batch_size}", flush=True)

    for batch_start in range(0, total_candidates, batch_size):
        batch_candidates = candidatePatterns_f[batch_start:batch_start+batch_size]
        print(f"   [Batch] 处理模式: {batch_start} ~ {batch_start+len(batch_candidates)-1} / {total_candidates}", flush=True)

        # 多进程并行计算
        print(f"   [模式] 多进程并行计算 (磁盘索引模式)", flush=True)
        pattern_event_compact, star_count = getFreqPatternsMultiProcess(
            batch_candidates, centerIndexEventNeiIndexMap_f, fpiThreshold, eventCount, idInstanceMap)

        # 基于累积的紧密度表计算当前批次的 FPI
        current_valid_count = 0
        for pattern, ecMap in pattern_event_compact.items():
            fpi = 1.0
            for event in pattern:
                if event not in ecMap:
                    fpi = 0.0
                    break
                eventCompactSum = sum(ecMap[event].values())
                curEventCount = eventCount[event]
                fpi = min(fpi, eventCompactSum / curEventCount)
                fpi = round(fpi, 4)
            if fpi >= fpiThreshold:
                pattern_Fpi[pattern] = fpi
                current_valid_count += 1

        print(f"   [Batch] 本批次发现频繁模式数量: {current_valid_count}", flush=True)

        # 定期清理：断开巨型字典引用，释放本批次的内存占用
        del pattern_event_compact
        gc.collect()

    print(f"   [FPI] 频繁模式总数量: {len(pattern_Fpi)}", flush=True)
    if len(pattern_Fpi) > 0:
        top5 = dict(sorted(pattern_Fpi.items(), key=lambda x: x[1], reverse=True)[:5])
        print(f"   [FPI] Top-5 模式: {top5}", flush=True)
    return pattern_Fpi


# 读取数据
if __name__ == "__main__":
    startTime = time.time()
    # FPI 核心参数
    fpiThreshold = 0.001
    memValueTheshold = 0.1
    absolutDistance = 20
    distanceThreshold = 5

    # 确定实际使用的进程数
    actual_processes = NUM_PROCESSES if NUM_PROCESSES is not None else cpu_count()
    print(f"[*] 参数配置: fpiThreshold={fpiThreshold}, MAX_NEI={MAX_NEI_PER_EVENT}, MAX_LEVEL={MAX_LEVEL}, 并行核心数={actual_processes}", flush=True)
    
    # ============ 运行模式配置 ============
    # 启用只读缓存机制与增量写入模式
    print("[*] 启动脚本，进入只读缓存和增量写入模式...", flush=True)

    index_exists = False
    # 缓存状态检测：识别当前目录下的索引文件
    if (os.path.exists("./temp_nei_index") or os.path.exists("./nei_index.db")) and \
       (os.path.exists("./mem_value_index") or os.path.exists("./mem_value_index.db")):
        index_exists = True

    if index_exists:
        print("[+] 检测到了磁盘索引，跳过距离计算和索引构建阶段", flush=True)
    else:
        # ============ 开始构建 ============
        print("[*] 开始读取数据并重新构建邻居关系（第一阶段运算可能需要很久）...", flush=True)

        # 生成邻居列表
        idInstanceMap, instanceIdMap, eventCount, event_instanceMap, chunk_files_returned, patternDisMap = \
            BasicToos2025070.getStarNei("./kunming_poi.data", absolutDistance, distanceThreshold, memValueTheshold, disfuncType=2)
        print(f"[+] 邻居构建完成，碎片文件数: {len(chunk_files_returned)}", flush=True)

        chunk_files = chunk_files_returned

    if not index_exists:
        # 构建星型邻居事件索引（分批处理 + 磁盘缓存，降低内存占用）
        print("[*] 开始组装全局星型候选人索引树 (分批磁盘缓存模式)", flush=True)
        
        BATCH_SIZE = 200  # 每批处理 200 个文件
        temp_cache_dir = "./temp_index_cache"
        os.makedirs(temp_cache_dir, exist_ok=True)
        temp_files = []
        
        num_batches = (len(chunk_files) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"   将 {len(chunk_files)} 个碎片文件分为 {num_batches} 批处理", flush=True)
        
        for batch_idx in range(num_batches):
            batch_start = batch_idx * BATCH_SIZE
            batch_end = min(batch_start + BATCH_SIZE, len(chunk_files))
            batch_files = chunk_files[batch_start:batch_end]
            
            print(f"   [批次 {batch_idx+1}/{num_batches}] 处理文件 {batch_start} ~ {batch_end-1}", flush=True)
            
            # 每批次独立构建部分索引
            partial_map = {}
            for idx, file in enumerate(batch_files):
                try:
                    with open(file, 'rb') as f:
                        local_pairs, _ = pickle.load(f)
                    for pat, pairs_dict in local_pairs.items():
                        for (cur, comp) in pairs_dict.keys():
                            if cur not in partial_map:
                                partial_map[cur] = set()
                            partial_map[cur].add(comp)
                    del local_pairs
                except Exception as e:
                    print(f"   [!] 文件 {file} 读取失败: {e}", flush=True)
            
            # 保存本批次结果到临时文件
            temp_file = os.path.join(temp_cache_dir, f"batch_{batch_idx}.pkl")
            with open(temp_file, 'wb') as f:
                pickle.dump(partial_map, f, protocol=pickle.HIGHEST_PROTOCOL)
            temp_files.append(temp_file)
            
            mem = psutil.virtual_memory()
            print(f"   [批次 {batch_idx+1}] 完成，本批次索引 {len(partial_map)} 个中心点 | 内存: {mem.percent}%", flush=True)
            
            # 释放本批次内存
            del partial_map
            gc.collect()
        
        # 流式合并：直接写入 shelve 数据库，不在内存中累积
        print("[*] 正在流式合并所有批次到磁盘索引（零内存累积模式）...", flush=True)
        
        # 创建临时 shelve 用于存储邻居索引
        temp_shelve_path = "./temp_nei_index"
        temp_db = shelve.open(temp_shelve_path, flag='n', protocol=pickle.HIGHEST_PROTOCOL, writeback=False)
        
        for batch_idx, temp_file in enumerate(temp_files):
            print(f"   -> 流式合并批次 {batch_idx+1}/{len(temp_files)}", flush=True)
            with open(temp_file, 'rb') as f:
                partial_map = pickle.load(f)
            
            # 直接写入 shelve，不在内存累积
            for cur, comp_set in partial_map.items():
                cur_key = str(cur)
                if cur_key in temp_db:
                    existing = set(temp_db[cur_key])
                    existing.update(comp_set)
                    temp_db[cur_key] = list(existing)
                else:
                    temp_db[cur_key] = list(comp_set)
            
            del partial_map
            temp_db.sync()  # 强制刷盘
            
            # 删除临时文件释放磁盘空间
            os.remove(temp_file)
            
            # 每3个批次监控一次
            if (batch_idx + 1) % 3 == 0:
                mem = psutil.virtual_memory()
                print(f"   -> 合并进度: {batch_idx+1}/{len(temp_files)} | 内存: {mem.percent}%", flush=True)
                gc.collect()
        
        # 将 shelve 重命名为永久邻居索引（不加载到内存）
        print("[*] 持久化邻居索引到磁盘...", flush=True)
        temp_db.close()
        
        # 重命名为永久索引（支持不同平台的 shelve 文件格式）
        rename_success = False
        
        # 尝试 .db 格式（大多数平台）
        if os.path.exists(temp_shelve_path + ".db"):
            try:
                if os.path.exists(NEI_INDEX_DB_PATH + ".db"):
                    os.remove(NEI_INDEX_DB_PATH + ".db")
                os.rename(temp_shelve_path + ".db", NEI_INDEX_DB_PATH + ".db")
                rename_success = True
                print(f"   -> 重命名成功: {temp_shelve_path}.db -> {NEI_INDEX_DB_PATH}.db", flush=True)
            except Exception as e:
                print(f"   [!] .db 格式重命名失败: {e}", flush=True)
        
        # 尝试 .dat/.bak/.dir 格式（某些 Unix 系统）
        if not rename_success:
            for ext in [".dat", ".bak", ".dir"]:
                if os.path.exists(temp_shelve_path + ext):
                    try:
                        if os.path.exists(NEI_INDEX_DB_PATH + ext):
                            os.remove(NEI_INDEX_DB_PATH + ext)
                        os.rename(temp_shelve_path + ext, NEI_INDEX_DB_PATH + ext)
                        rename_success = True
                        print(f"   -> 重命名成功: {temp_shelve_path}{ext} -> {NEI_INDEX_DB_PATH}{ext}", flush=True)
                    except Exception as e:
                        print(f"   [!] {ext} 格式重命名失败: {e}", flush=True)
        
        if not rename_success:
            print(f"   [!] 警告：未找到临时 shelve 文件，尝试直接使用临时路径", flush=True)
            NEI_INDEX_DB_PATH = temp_shelve_path
        
        # 清理临时目录
        try:
            os.rmdir(temp_cache_dir)
        except:
            pass
    
    # 无论是复用还是新构建，都在这里统一读取基础数据结构(因为 getFreqPatterns 需要用到 eventCount 等)
    if index_exists:
        try:
            print("[*] 为确保上下文完整，正在从本地 kunming_poi.data 快速还原基础实例结构映射...", flush=True)
            idInstanceMap, instanceIdMap, eventCount, event_instanceMap, chunk_files, patternDisMap = \
                BasicToos2025070.getStarNei("./kunming_poi.data", absolutDistance, distanceThreshold, memValueTheshold, disfuncType=2)
            # 拿到映射数据后直接打断写入流，因为不需要再写一遍
        except Exception as e:
            print(f"   [!] 重建基础实例结构时发生错误: {e}")

    # 以只读模式打开邻居索引
    centerIndexEventNeiIndexMap = shelve.open(NEI_INDEX_DB_PATH, flag='r', protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[+] 邻居索引就绪，共 {len(centerIndexEventNeiIndexMap)} 个中心点（磁盘模式）", flush=True)

    # ============ 构建/加载磁盘索引 ============
    print("\n[*] 加载磁盘隶属度索引...", flush=True)
    # 如果已存在，build_shelve_index 会自动识别并以读取模式返回
    mem_db = build_shelve_index(chunk_files, force_rebuild=False)
    print(f"[+] 磁盘索引就绪", flush=True)
    gc.collect()

    # ============ 2 阶模式挖掘 ============
    current_level = 2
    print(f"\n[*] === 第 {current_level} 阶模式挖掘 ===", flush=True)
    candidatePatterns = genCandidatePatterns(list(eventCount.keys()))
    print(f"   候选模式数: {len(candidatePatterns)}", flush=True)

    patternFpi = getFreqPatterns(candidatePatterns, centerIndexEventNeiIndexMap, mem_db)
    gc.collect()

    sorted_patternFpi = dict(sorted(patternFpi.items(), key=lambda item: item[1], reverse=True))
    print(f"[+] 2阶频繁模式数量: {len(sorted_patternFpi)}", flush=True)

    # 收集所有阶的频繁模式
    allFreqPatterns = dict(sorted_patternFpi)

    # ============ 逐阶扩展 ============
    while len(patternFpi) > 0:
        current_level += 1
        # 阶数上限检查
        if MAX_LEVEL is not None and current_level > MAX_LEVEL:
            print(f"\n[!] 已达到最大扩展阶数 {MAX_LEVEL}，停止扩展", flush=True)
            break

        print(f"\n[*] === 第 {current_level} 阶模式挖掘 ===", flush=True)
        candidatePatterns = genCandidatePatterns(list(patternFpi.keys()))
        print(f"   候选模式数: {len(candidatePatterns)}", flush=True)

        if len(candidatePatterns) == 0:
            print("   无候选模式，扩展结束", flush=True)
            break

        patternFpi = getFreqPatterns(candidatePatterns, centerIndexEventNeiIndexMap, mem_db)
        gc.collect()

        sorted_patternFpi = dict(sorted(patternFpi.items(), key=lambda item: item[1], reverse=True))
        print(f"[+] {current_level}阶频繁模式数量: {len(sorted_patternFpi)}", flush=True)
        allFreqPatterns.update(sorted_patternFpi)

    # ============ 关闭磁盘索引 ============
    try:
        mem_db.close()
    except Exception:
        pass
    
    try:
        centerIndexEventNeiIndexMap.close()
    except Exception:
        pass

    # ============ 输出汇总 ============
    endTime = time.time()
    print(f"\n{'='*60}", flush=True)
    print(f"[+] Joinless 算法执行完成", flush=True)
    print(f"    总耗时: {endTime-startTime:.2f} 秒", flush=True)
    print(f"    发现频繁模式总数: {len(allFreqPatterns)}", flush=True)
    print(f"    最高扩展阶数: {current_level}", flush=True)
    if len(allFreqPatterns) > 0:
        sortedAll = dict(sorted(allFreqPatterns.items(), key=lambda x: x[1], reverse=True))
        print(f"    Top-10 频繁模式:", flush=True)
        for i, (p, fpi) in enumerate(list(sortedAll.items())[:10]):
            print(f"      {i+1}. {p} -> FPI={fpi}", flush=True)
    print(f"{'='*60}", flush=True)

    # 算法执行完毕，保留碎片文件、缓存和磁盘索引以便下次运行时重用
    print(f"[*] 跑通完成，保留底层的碎片文件、临时缓存和磁盘索引...", flush=True)

    # ================= 新增大屏所需文件输出逻辑 =================
    import json
    import pandas as pd
    
    print(f"\n[*] 开始导出大屏系统所需的高阶可视化文件...", flush=True)

    # 1. 导出排行榜 CSV
    high_order_patterns = []
    pattern_id_counter = 1
    
    # 筛选只包含 3 阶及以上的模式 (长度 >= 3 表示至少3个字符的组合)
    high_order_dict = {p: fpi for p, fpi in allFreqPatterns.items() if len(p) >= 3}
    
    sorted_high_order = dict(sorted(high_order_dict.items(), key=lambda x: x[1], reverse=True))

    for pattern, fpi in sorted_high_order.items():
        high_order_patterns.append({
            "pattern_id": "H_" + str(pattern_id_counter),
            "pattern_name": pattern,
            "fpi_score": fpi,
            "level": len(pattern)
        })
        pattern_id_counter += 1

    if len(high_order_patterns) > 0:
        high_order_df = pd.DataFrame(high_order_patterns)
        high_order_df.to_csv("./higher_order_fpi_patterns.csv", index=False)
        print(f"   [+] 成功导出高阶模式榜单: higher_order_fpi_patterns.csv ({len(high_order_patterns)} 条记录)")
    else:
        print(f"   [-] 未挖掘出 3 阶及以上的高阶模式，跳过导出。")

    # 2. 导出高阶模式空间映射坐标 JSON
    print(f"   [!] 大屏地理引擎绘图所需的微观坐标系文件 (pattern_instances.json) 已由底层 BasicToos2025070 提供。高阶仅提供统计排行版 CSV 文件补充左右侧看板。")
    print(f"[*] 所有阶段执行结束。")
    # ==========================================================

    '''
    x = [i for i in patternDisMap["HJ"].values()]
    valueFreqFloatMap = {}
    valueFreqMap = {}
    for value in x:
        value = round(value * 0.1) / float(0.1)
        freq = valueFreqMap.get(value, 0)
        freq += 1
        valueFreqMap[value] = freq
    valueFreqFloatMap = [(value, valueFreqMap[value] / len(x)) for value in valueFreqMap.keys()]
    x = [i[0] for i in valueFreqFloatMap]
    y = [round(i[1], 2) for i in valueFreqFloatMap]

    BasicTools.drawBar(10, x, y, "", "Distance", "Frequency", "the frequency of distances")
    print("选定模式对应的实例距离出现频率为：", valueFreqMap)

    patternFpiPairList = list(patternFpi.items())
    patternFpiPairList.sort(key=lambda i:i[1],reverse=True)
    print("模式对应的参与度为", patternFpiPairList)
    #将模式对应的FPI存入CSV文件中
    patternFpiDf = pd.DataFrame(patternFpiPairList)
    patternFpiDf.to_csv("FPIPatternPi.csv")
    barInter = 0.025
    interValues, patternPiMap = BasicTools.getIntervalData(patternFpi, barInter)
    # 将频率按pi值大小排序后存入表中
    valueFreqMap= BasicTools.getFreq(interValues,eventCount,patternPiMap)
    valueFreqPair = list(valueFreqMap.items())
    valueFreqPair.sort(key=lambda i: i[0])
    patternFpiDf = pd.DataFrame(valueFreqPair)
    patternFpiDf.to_csv("FPIPiFreq.csv")
    print("模式对应的频率为：", valueFreqPair)
    x = [i[0] for i in valueFreqPair]
    y = [i[1] for i in valueFreqPair]
    print(x, y)
    plt.bar(x, y, width=barInter + barInter / 100, facecolor='yellowgreen', edgecolor='white')
    plt.xticks()
    #图例
    plt.legend(["the frequency of FPI"])
    #设置x轴范围值
    plt.xlim([0,max(x)])
    #设置x轴标签
    plt.xlabel("FPI")
    # 设置y轴标签
    plt.ylabel("Frequency")
    #plt.title("FPI")
    plt.show()

    # patternDisMap存储了:{模式名称：{被比较对象的ID：距离}}
    x = [int(i / 10) * 10 for i in patternDisMap["BE"].values()]
    y = [i for i in range(len(x))]
    # 利用python自带的计数器进行计数
    from collections import Counter

    counter = Counter(x)
    distance_values = counter.keys()  # 距离的值
    occur_times = counter.values()  # 每个距离值出现的次数
    times_sum = sum(occur_times)  # 出现的总次数
    distance_freq = [i_list / float(times_sum) for i_list in occur_times]  # 出现距离的频率
    print(distance_freq)

    print("y距离的个数", y)
    print('x距离的数据', x)
    BasicTools.drawBar(10, distance_values, distance_freq, "", "distance", "frequency", "frequency of distance")

    plt.show()
    import csv
    out = open("patternDis.csv", 'a', newline='')
    csv_write = csv.writer(out,dialect="excel")
    csv_write.writerow(patternDisMap.items())
    '''
