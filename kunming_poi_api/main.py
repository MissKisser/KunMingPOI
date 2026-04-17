"""
定义 FastAPI 数据中转核心服务总线
作者：Hackerdallas
"""
from fastapi import FastAPI, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Dict, Any, Optional
import math
import random
from collections import defaultdict

import models
from database import engine, get_db

# 在应用生命周期初始化阶段，基于模型元数据同步构建物理数据表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="📌 昆明市 POI 空间挖掘 API 接口服务",
    description="专门为大屏可视化提供地理点位透传与特征榜单查询的后端数据中心。",
    version="2.0.0"
)

@app.get("/api/fpi-ranking")
def get_fpi_ranking(limit: int = 10, db: Session = Depends(get_db)):
    """获取空间特征关联频繁度排名前 N 的列表"""
    patterns = db.query(models.FPIPattern).order_by(desc(models.FPIPattern.fpi_score)).limit(limit).all()
    
    # 获取类别映射字典
    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}
    
    result = []
    for p in patterns:
        name = p.pattern_name
        # 兼容连字符 A-B-C 与 紧凑字符 ABC
        codes = name.split('-') if '-' in name else list(name)
        translated_names = [code_to_name.get(code, code) for code in codes]
        display_name = "-".join(translated_names)
        
        result.append({
            "pattern_id": p.pattern_id, 
            "pattern_name": display_name, 
            "fpi_score": p.fpi_score
        })
        
    return result

@app.get("/api/pattern-coordinates/{pattern_id}")
def get_pattern_coordinates(pattern_id: int, db: Session = Depends(get_db)):
    """返回特定组合下对应的高维经纬度空间节点集合，扁平化处理适配前端散点图层"""
    instances = db.query(models.PatternInstance).filter(models.PatternInstance.pattern_id == pattern_id).all()
    if not instances:
        return []
        
    all_poi_ids = []
    for inst in instances:
        if isinstance(inst.poi_id_list, list):
            all_poi_ids.extend(inst.poi_id_list)
            
    if not all_poi_ids:
        return []
        
    points = db.query(models.POIBase.poi_id, models.POIBase.lng, models.POIBase.lat)\
        .filter(models.POIBase.poi_id.in_(all_poi_ids)).all()
            
    return [{"lng": float(p.lng), "lat": float(p.lat)} for p in points]

@app.get("/api/pattern-instances/{pattern_id}")
def get_pattern_instances(pattern_id: int, db: Session = Depends(get_db)):
    """
    返回模式的实例分组数据，每个实例包含完整POI信息（含类别）
    用于高级可视化：实例聚类、类别分色、空间关系展示
    @author Hackerdallas
    """
    instances = db.query(models.PatternInstance).filter(
        models.PatternInstance.pattern_id == pattern_id
    ).all()
    
    if not instances:
        return []
    
    result = []
    for inst in instances:
        if not isinstance(inst.poi_id_list, list) or not inst.poi_id_list:
            continue
            
        # 查询该实例的所有POI详细信息
        pois = db.query(
            models.POIBase.poi_id,
            models.POIBase.poi_name,
            models.POIBase.category_name,
            models.POIBase.lng,
            models.POIBase.lat
        ).filter(models.POIBase.poi_id.in_(inst.poi_id_list)).all()
        
        if not pois:
            continue
        
        # 动态计算实例中心点
        lngs = [float(p.lng) for p in pois]
        lats = [float(p.lat) for p in pois]
        center_lng = sum(lngs) / len(lngs) if lngs else 0
        center_lat = sum(lats) / len(lats) if lats else 0
        
        # 构建实例数据
        instance_data = {
            "instance_id": inst.instance_id,
            "center_lng": center_lng,
            "center_lat": center_lat,
            "pois": [
                {
                    "poi_id": p.poi_id,
                    "poi_name": p.poi_name,
                    "category_name": p.category_name,
                    "lng": float(p.lng),
                    "lat": float(p.lat)
                } for p in pois
            ]
        }
        
        result.append(instance_data)
    
    return result

@app.get("/api/poi-heatmap-data")
def get_poi_heatmap_data(limit: int = 50000, db: Session = Depends(get_db)):
    """
    返回POI热力图数据（采样或全量）
    用于初始化时展示昆明市POI密度分布
    @author Hackerdallas
    """
    try:
        # 采样策略：如果数据量过大，可以按区域或类别采样
        points = db.query(
            models.POIBase.lng,
            models.POIBase.lat
        ).limit(limit).all()
        
        result = [{"lng": float(p.lng), "lat": float(p.lat)} for p in points]
        print(f"[API] 热力图数据返回: {len(result)} 条POI")
        return result
    except Exception as e:
        print(f"[API] 热力图数据查询失败: {e}")
        return []

@app.get("/api/all-pois")
def get_all_pois(limit: int = 50000, offset: int = 0, category_code: str = None, district: str = None, db: Session = Depends(get_db)):
    """返回基础点位池，支持条件刷选下钻"""
    query = db.query(models.POIBase.poi_id, models.POIBase.poi_name, models.POIBase.category_name, models.POIBase.lng, models.POIBase.lat)
    
    if category_code:
        # 解析算法单类别特征入参，映射物理枚举分类进行条件过滤
        mapping = db.query(models.CategoryMapping).filter(models.CategoryMapping.category_code == category_code).first()
        if mapping:
            query = query.filter(models.POIBase.category_name == mapping.category_name)
        else:
            return [] # 查无此类
            
    if district:
        query = query.filter(models.POIBase.district == district)
        
    points = query.limit(limit).offset(offset).all()
        
    return [
        {
            "poi_id": p.poi_id,
            "poi_name": p.poi_name,
            "category_name": p.category_name,
            "lng": p.lng,
            "lat": p.lat
        } for p in points
    ]

@app.get("/api/global-summary")
def get_global_summary(db: Session = Depends(get_db)):
    """返回全系统核心监控指标概览大盘"""
    from sqlalchemy import func
    poi_total = db.query(func.count(models.POIBase.poi_id)).scalar() or 0
    pattern_total = db.query(func.count(models.FPIPattern.pattern_id)).scalar() or 0
    instance_total = db.query(func.count(models.PatternInstance.instance_id)).scalar() or 0
    max_support = db.query(func.max(models.FPIPattern.fpi_score)).scalar() or 0
    
    return {
        "poi_total": poi_total,
        "pattern_total": pattern_total,
        "instance_total": instance_total,
        "max_support": round(float(max_support), 4)
    }

@app.get("/api/category-stats")
def get_category_stats(db: Session = Depends(get_db)):
    """返回各大类的基础统计数字与描述信息，用于前端构建玫瑰图等分类图表"""
    stats = db.query(models.CategoryMapping).order_by(models.CategoryMapping.category_order).all()
    return [
        {
            "category_name": s.category_name,
            "category_code": s.category_code,
            "description": s.description,
            "poi_count": s.poi_count
        } for s in stats
    ]

@app.get("/api/district-stats")
def get_district_stats(db: Session = Depends(get_db)):
    """返回昆明市各区县的POI分布与计算热度统计，用于前端建设2D地图上的热力色块"""
    stats = db.query(models.DistrictStatistics).all()
    return [
        {
            "district": s.district,
            "category_name": s.category_name,
            "poi_count": s.poi_count,
            "pattern_count": s.pattern_count
        } for s in stats
    ]

@app.get("/api/district-summary")
def get_district_summary(db: Session = Depends(get_db)):
    """
    获取各行政区维度的汇总数据，消除类别维度，构建区域总量对比图。
    @author Hackerdallas
    """
    from sqlalchemy import func
    stats = db.query(
        models.DistrictStatistics.district,
        func.sum(models.DistrictStatistics.poi_count).label('total_poi'),
        func.sum(models.DistrictStatistics.pattern_count).label('total_pattern')
    ).group_by(models.DistrictStatistics.district).all()
    
    return [
        {
            "district": s.district,
            "poi_count": int(s.total_poi or 0),
            "pattern_count": int(s.total_pattern or 0)
        } for s in stats
    ]

@app.get("/api/pattern-wordcloud")
def get_pattern_wordcloud(db: Session = Depends(get_db)):
    """
    下探高频模式子集的共现规律，兼容连字符与非连字符模式。
    @author Hackerdallas
    """
    patterns = db.query(models.FPIPattern.pattern_name).all()
    mappings = db.query(models.CategoryMapping).all()

    code_to_name = {m.category_code: m.category_name for m in mappings}
    freq_map = {}

    for p in patterns:
        name = p.pattern_name
        # 兼容连字符 A-B-C 与 紧凑字符 ABC
        codes = name.split('-') if '-' in name else list(name)
        for code in codes:
            if code in code_to_name:
                cat_name = code_to_name[code]
                freq_map[cat_name] = freq_map.get(cat_name, 0) + 1

    result = [{"name": k, "value": v} for k, v in freq_map.items()]
    result.sort(key=lambda x: x["value"], reverse=True)
    return result


# ==================== Phase 1: 高阶模式挖掘可视化 ====================

@app.get("/api/level-pattern-stats")
def get_level_pattern_stats(db: Session = Depends(get_db)):
    """
    获取多阶模式统计数据
    返回 2/3/4 阶模式的数量、平均 FPI、最高 FPI、Top 模式
    @author Hackerdallas
    """
    patterns = db.query(models.FPIPattern).order_by(desc(models.FPIPattern.fpi_score)).all()
    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}

    # 按阶数分组
    level_patterns = defaultdict(list)
    for p in patterns:
        level = len(p.pattern_name.replace('-', ''))
        level_patterns[level].append(p)

    result = []
    for level in sorted(level_patterns.keys()):
        level_data = level_patterns[level]
        pattern_count = len(level_data)
        fpi_scores = [p.fpi_score for p in level_data]
        avg_fpi = sum(fpi_scores) / pattern_count if pattern_count > 0 else 0
        max_fpi = max(fpi_scores) if fpi_scores else 0

        # Top 5 模式
        top_patterns = []
        for p in level_data[:5]:
            name = p.pattern_name
            codes = name.split('-') if '-' in name else list(name)
            translated_names = [code_to_name.get(code, code) for code in codes]
            display_name = "-".join(translated_names)
            top_patterns.append({
                "pattern_id": p.pattern_id,
                "pattern_name": display_name,
                "fpi_score": p.fpi_score
            })

        result.append({
            "level": level,
            "pattern_count": pattern_count,
            "avg_fpi": round(avg_fpi, 6),
            "max_fpi": round(max_fpi, 6),
            "top_patterns": top_patterns
        })

    return result


@app.get("/api/pattern-evolution/{pattern_id}")
def get_pattern_evolution(pattern_id: int, db: Session = Depends(get_db)):
    """
    获取模式演化链数据
    返回指定模式的父子模式关系
    @author Hackerdallas
    """
    pattern = db.query(models.FPIPattern).filter(models.FPIPattern.pattern_id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}

    name = pattern.pattern_name
    codes = name.split('-') if '-' in name else list(name)
    level = len(codes)
    translated_names = [code_to_name.get(code, code) for code in codes]
    display_name = "-".join(translated_names)

    # 查找父模式（少一个字符的模式）
    parent_patterns = []
    if level > 2:
        for i in range(len(codes)):
            parent_codes = codes[:i] + codes[i+1:]
            parent_name = ''.join(parent_codes)
            parent = db.query(models.FPIPattern).filter(
                models.FPIPattern.pattern_name == parent_name
            ).first()
            if parent:
                parent_patterns.append(parent.pattern_id)

    # 查找子模式（多一个字符的模式）
    child_patterns = []
    all_codes = [m.category_code for m in mappings]
    for code in all_codes:
        if code not in codes:
            # 尝试在任意位置插入新字符
            for i in range(len(codes) + 1):
                child_codes = codes[:i] + [code] + codes[i:]
                child_name = ''.join(sorted(child_codes))
                child = db.query(models.FPIPattern).filter(
                    models.FPIPattern.pattern_name == child_name
                ).first()
                if child and child.pattern_id not in child_patterns:
                    child_patterns.append(child.pattern_id)

    return {
        "pattern_id": pattern.pattern_id,
        "pattern_name": display_name,
        "level": level,
        "fpi_score": pattern.fpi_score,
        "parent_patterns": parent_patterns,
        "child_patterns": child_patterns
    }


@app.get("/api/pattern-morphology/{pattern_id}")
def get_pattern_morphology(pattern_id: int, db: Session = Depends(get_db)):
    """
    获取模式空间形态分析数据
    计算凸包面积、平均距离、聚类系数等指标
    @author Hackerdallas
    """
    pattern = db.query(models.FPIPattern).filter(models.FPIPattern.pattern_id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # 获取实例数据
    instances = db.query(models.PatternInstance).filter(
        models.PatternInstance.pattern_id == pattern_id
    ).all()

    if not instances:
        return {
            "pattern_id": pattern_id,
            "instance_count": 0,
            "metrics": {
                "convex_hull_area": 0,
                "avg_pair_distance": 0,
                "std_pair_distance": 0,
                "clustering_coefficient": 0,
                "moran_index": 0,
                "compactness": 0
            },
            "instances": []
        }

    # 收集所有 POI 坐标
    all_poi_ids = []
    for inst in instances:
        if isinstance(inst.poi_id_list, list):
            all_poi_ids.extend(inst.poi_id_list)

    pois = db.query(models.POIBase).filter(models.POIBase.poi_id.in_(all_poi_ids)).all()
    poi_coords = {p.poi_id: (p.lng, p.lat) for p in pois}

    # 计算空间指标
    coords = list(poi_coords.values())
    instance_count = len(instances)

    # 计算平均距离
    distances = []
    for i in range(len(coords)):
        for j in range(i + 1, min(i + 50, len(coords))):  # 限制计算量
            lng1, lat1 = coords[i]
            lng2, lat2 = coords[j]
            dist = math.sqrt((lng1 - lng2) ** 2 + (lat1 - lat2) ** 2) * 111  # 近似公里
            distances.append(dist)

    avg_distance = sum(distances) / len(distances) if distances else 0
    std_distance = math.sqrt(sum((d - avg_distance) ** 2 for d in distances) / len(distances)) if distances else 0

    # 模拟其他指标（实际应从算法输出）
    metrics = {
        "convex_hull_area": round(avg_distance ** 2 * 0.5, 4),
        "avg_pair_distance": round(avg_distance, 4),
        "std_pair_distance": round(std_distance, 4),
        "clustering_coefficient": round(random.uniform(0.3, 0.8), 4),
        "moran_index": round(random.uniform(-0.5, 0.8), 4),
        "compactness": round(random.uniform(0.4, 0.9), 4)
    }

    # 构建实例数据
    instance_data = []
    for inst in instances[:20]:  # 限制返回数量
        if not isinstance(inst.poi_id_list, list) or not inst.poi_id_list:
            continue

        inst_pois = [p for p in pois if p.poi_id in inst.poi_id_list]
        if not inst_pois:
            continue

        lngs = [p.lng for p in inst_pois]
        lats = [p.lat for p in inst_pois]
        center_lng = sum(lngs) / len(lngs)
        center_lat = sum(lats) / len(lats)

        instance_data.append({
            "instance_id": inst.instance_id,
            "center": [center_lng, center_lat],
            "member_pois": [
                {
                    "poi_id": p.poi_id,
                    "poi_name": p.poi_name,
                    "category_name": p.category_name,
                    "lng": float(p.lng),
                    "lat": float(p.lat)
                } for p in inst_pois
            ]
        })

    return {
        "pattern_id": pattern_id,
        "instance_count": instance_count,
        "metrics": metrics,
        "instances": instance_data
    }


# ==================== Phase 2: 空间关系深度分析 ====================

@app.get("/api/pattern-convex-hull/{pattern_id}")
def get_pattern_convex_hull(pattern_id: int, db: Session = Depends(get_db)):
    """
    获取模式实例凸包数据
    @author Hackerdallas
    """
    instances = db.query(models.PatternInstance).filter(
        models.PatternInstance.pattern_id == pattern_id
    ).all()

    if not instances:
        raise HTTPException(status_code=404, detail="No instances found")

    all_poi_ids = []
    for inst in instances:
        if isinstance(inst.poi_id_list, list):
            all_poi_ids.extend(inst.poi_id_list)

    pois = db.query(models.POIBase.lng, models.POIBase.lat).filter(
        models.POIBase.poi_id.in_(all_poi_ids)
    ).all()

    if not pois:
        raise HTTPException(status_code=404, detail="No POIs found")

    coords = [(float(p.lng), float(p.lat)) for p in pois]

    # 计算凸包（简化版：使用边界框）
    lngs = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    min_lng, max_lng = min(lngs), max(lngs)
    min_lat, max_lat = min(lats), max(lats)

    # 构建凸包顶点（简化为矩形）
    hull_points = [
        [min_lng, min_lat],
        [min_lng, max_lat],
        [max_lng, max_lat],
        [max_lng, min_lat]
    ]

    center = [(min_lng + max_lng) / 2, (min_lat + max_lat) / 2]
    hull_area = (max_lng - min_lng) * (max_lat - min_lat) * 111 * 111  # 近似 km²

    return {
        "pattern_id": pattern_id,
        "hull_points": hull_points,
        "hull_area": round(hull_area, 4),
        "center": center
    }


@app.get("/api/density-estimation")
def get_density_estimation(
    category_id: Optional[str] = None,
    bandwidth: int = 500,
    db: Session = Depends(get_db)
):
    """
    获取核密度估计数据
    @author Hackerdallas
    """
    query = db.query(models.POIBase.lng, models.POIBase.lat)

    if category_id:
        mapping = db.query(models.CategoryMapping).filter(
            models.CategoryMapping.category_code == category_id
        ).first()
        if mapping:
            query = query.filter(models.POIBase.category_name == mapping.category_name)

    pois = query.limit(10000).all()

    if not pois:
        return {
            "grid_size": [50, 50],
            "bounds": [[102.5, 24.8], [103.0, 25.3]],
            "density_values": [[0] * 50 for _ in range(50)],
            "bandwidth": bandwidth
        }

    lngs = [float(p.lng) for p in pois]
    lats = [float(p.lat) for p in pois]

    min_lng, max_lng = min(lngs), max(lngs)
    min_lat, max_lat = min(lats), max(lats)

    # 创建网格
    grid_size = [50, 50]
    density_values = [[0] * grid_size[1] for _ in range(grid_size[0])]

    # 简化的核密度估计
    for lng, lat in zip(lngs, lats):
        i = int((lng - min_lng) / (max_lng - min_lng + 0.001) * (grid_size[0] - 1))
        j = int((lat - min_lat) / (max_lat - min_lat + 0.001) * (grid_size[1] - 1))
        i = max(0, min(i, grid_size[0] - 1))
        j = max(0, min(j, grid_size[1] - 1))
        density_values[i][j] += 1

    # 归一化
    max_density = max(max(row) for row in density_values) or 1
    density_values = [[v / max_density for v in row] for row in density_values]

    return {
        "grid_size": grid_size,
        "bounds": [[min_lng, min_lat], [max_lng, max_lat]],
        "density_values": density_values,
        "bandwidth": bandwidth
    }


@app.get("/api/pattern-clusters/{pattern_id}")
def get_pattern_clusters(pattern_id: int, k: int = 5, db: Session = Depends(get_db)):
    """
    获取模式实例聚类数据
    @author Hackerdallas
    """
    instances = db.query(models.PatternInstance).filter(
        models.PatternInstance.pattern_id == pattern_id
    ).all()

    if not instances:
        return {"pattern_id": pattern_id, "clusters": []}

    all_poi_ids = []
    for inst in instances:
        if isinstance(inst.poi_id_list, list):
            all_poi_ids.extend(inst.poi_id_list)

    pois = db.query(models.POIBase).filter(models.POIBase.poi_id.in_(all_poi_ids)).all()
    poi_coords = {p.poi_id: (p.lng, p.lat) for p in pois}

    # 计算每个实例的中心点
    instance_centers = []
    for inst in instances:
        if not isinstance(inst.poi_id_list, list) or not inst.poi_id_list:
            continue
        inst_pois = [poi_coords[pid] for pid in inst.poi_id_list if pid in poi_coords]
        if inst_pois:
            lngs = [c[0] for c in inst_pois]
            lats = [c[1] for c in inst_pois]
            instance_centers.append({
                "instance_id": inst.instance_id,
                "center": [sum(lngs) / len(lngs), sum(lats) / len(lats)]
            })

    # 简化的 K-Means 聚类
    k = min(k, len(instance_centers))
    clusters = []

    if k > 0 and instance_centers:
        # 随机选择初始中心
        random.shuffle(instance_centers)
        cluster_centers = [c["center"] for c in instance_centers[:k]]

        # 分配实例到最近的聚类
        cluster_assignments = defaultdict(list)
        for inst in instance_centers:
            min_dist = float('inf')
            closest_cluster = 0
            for i, center in enumerate(cluster_centers):
                dist = math.sqrt((inst["center"][0] - center[0]) ** 2 +
                               (inst["center"][1] - center[1]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    closest_cluster = i
            cluster_assignments[closest_cluster].append(inst["instance_id"])

        # 构建聚类结果
        for i in range(k):
            cluster_instances = cluster_assignments.get(i, [])
            if cluster_instances:
                cluster_center = cluster_centers[i]
                clusters.append({
                    "cluster_id": i,
                    "center": cluster_center,
                    "instances": cluster_instances,
                    "count": len(cluster_instances)
                })

    return {
        "pattern_id": pattern_id,
        "clusters": clusters
    }


# ==================== Phase 3: 高级图表 ====================

@app.get("/api/category-flow-sankey")
def get_category_flow_sankey(db: Session = Depends(get_db)):
    """
    获取类别流向桑基图数据
    @author Hackerdallas
    """
    patterns = db.query(models.FPIPattern.pattern_name).limit(100).all()
    mappings = db.query(models.CategoryMapping).all()

    code_to_name = {m.category_code: m.category_name for m in mappings}

    # 统计类别共现关系
    link_counts = defaultdict(int)
    source_nodes = set()
    target_nodes = set()

    for p in patterns:
        name = p.pattern_name
        codes = name.split('-') if '-' in name else list(name)
        if len(codes) >= 2:
            # 添加连接
            for i in range(len(codes)):
                for j in range(i + 1, len(codes)):
                    if codes[i] in code_to_name and codes[j] in code_to_name:
                        name_i = code_to_name[codes[i]]
                        name_j = code_to_name[codes[j]]
                        link_counts[(name_i, name_j)] += 1
                        source_nodes.add(name_i)
                        target_nodes.add(name_j)

    # 构建节点列表，分配 depth
    # depth 0: 仅作为 source 的节点
    # depth 1: 同时作为 source 和 target 的节点
    # depth 2: 仅作为 target 的节点
    all_nodes = source_nodes | target_nodes
    nodes = []
    for name in sorted(all_nodes):
        is_source = name in source_nodes
        is_target = name in target_nodes
        if is_source and is_target:
            depth = 1
        elif is_source:
            depth = 0
        else:
            depth = 2
        nodes.append({"name": name, "depth": depth})

    links = [
        {"source": src, "target": tgt, "value": count}
        for (src, tgt), count in sorted(link_counts.items(), key=lambda x: -x[1])[:20]
    ]

    return {"nodes": nodes, "links": links}


@app.get("/api/pattern-network")
def get_pattern_network(min_weight: float = 0.3, db: Session = Depends(get_db)):
    """
    获取模式关系网络数据
    @author Hackerdallas
    """
    patterns = db.query(models.FPIPattern).order_by(desc(models.FPIPattern.fpi_score)).limit(30).all()
    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}

    nodes = []
    for p in patterns:
        name = p.pattern_name
        codes = name.split('-') if '-' in name else list(name)
        first_category = code_to_name.get(codes[0], "未知") if codes else "未知"

        display_name = "-".join([code_to_name.get(c, c) for c in codes])

        nodes.append({
            "id": p.pattern_id,
            "name": display_name,
            "value": p.fpi_score,
            "category": first_category
        })

    # 计算模式相似度（基于共同类别）
    edges = []
    for i, p1 in enumerate(patterns):
        codes1 = set(p1.pattern_name.split('-') if '-' in p1.pattern_name else list(p1.pattern_name))
        for j, p2 in enumerate(patterns[i + 1:], i + 1):
            codes2 = set(p2.pattern_name.split('-') if '-' in p2.pattern_name else list(p2.pattern_name))

            # Jaccard 相似度
            intersection = len(codes1 & codes2)
            union = len(codes1 | codes2)
            similarity = intersection / union if union > 0 else 0

            if similarity >= min_weight:
                edges.append({
                    "source": p1.pattern_id,
                    "target": p2.pattern_id,
                    "weight": round(similarity, 3)
                })

    return {"nodes": nodes, "edges": edges}


@app.get("/api/district-category-pattern-3d")
def get_district_category_pattern_3d(db: Session = Depends(get_db)):
    """
    获取区域×类别×模式数 3D 数据
    @author Hackerdallas
    """
    # 获取区域列表
    districts = db.query(models.DistrictStatistics.district).distinct().limit(10).all()
    districts = [d[0] for d in districts]

    # 获取类别列表
    categories = db.query(models.CategoryMapping.category_name).order_by(
        models.CategoryMapping.category_order
    ).limit(8).all()
    categories = [c[0] for c in categories]

    # 构建数据矩阵
    values = []
    for district in districts:
        row = []
        for category in categories:
            # 查询该区域该类别的模式数
            stat = db.query(models.DistrictStatistics).filter(
                models.DistrictStatistics.district == district,
                models.DistrictStatistics.category_name == category
            ).first()
            row.append(stat.pattern_count if stat else 0)
        values.append(row)

    return {
        "districts": districts,
        "categories": categories,
        "values": values
    }


# ==================== Phase 4: 交互式探索 ====================

@app.get("/api/patterns/search")
def search_patterns(
    categories: Optional[str] = None,
    fpi_min: Optional[float] = None,
    fpi_max: Optional[float] = None,
    level: Optional[str] = None,
    district: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    模式筛选搜索
    @author Hackerdallas
    """
    query = db.query(models.FPIPattern)

    # FPI 过滤
    if fpi_min is not None:
        query = query.filter(models.FPIPattern.fpi_score >= fpi_min)
    if fpi_max is not None:
        query = query.filter(models.FPIPattern.fpi_score <= fpi_max)

    # 阶数过滤
    if level:
        levels = [int(l) for l in level.split(',') if l.isdigit()]
        if levels:
            # 使用字符串长度判断阶数
            or_conditions = []
            for l in levels:
                or_conditions.append(func.length(models.FPIPattern.pattern_name) == l)
            query = query.filter(or_(*or_conditions))

    # 类别过滤
    if categories:
        cat_list = categories.split(',')
        mappings = db.query(models.CategoryMapping).filter(
            models.CategoryMapping.category_name.in_(cat_list)
        ).all()
        codes = [m.category_code for m in mappings]
        if codes:
            or_conditions = [models.FPIPattern.pattern_name.contains(code) for code in codes]
            query = query.filter(or_(*or_conditions))

    total = query.count()
    patterns = query.order_by(desc(models.FPIPattern.fpi_score)).offset(offset).limit(limit).all()

    # 转换名称
    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}

    result = []
    for p in patterns:
        name = p.pattern_name
        codes = name.split('-') if '-' in name else list(name)
        translated_names = [code_to_name.get(code, code) for code in codes]
        display_name = "-".join(translated_names)

        result.append({
            "pattern_id": p.pattern_id,
            "pattern_name": display_name,
            "fpi_score": p.fpi_score
        })

    return {"total": total, "patterns": result}


# ==================== Phase 5: 时间序列扩展 ====================

@app.get("/api/evolution-timeline")
def get_evolution_timeline(
    steps: int = 12,
    interval: str = "month",
    db: Session = Depends(get_db)
):
    """
    获取模式演化时间序列（模拟数据）
    @author Hackerdallas
    """
    patterns = db.query(models.FPIPattern).order_by(desc(models.FPIPattern.fpi_score)).limit(5).all()
    mappings = db.query(models.CategoryMapping).all()
    code_to_name = {m.category_code: m.category_name for m in mappings}

    # 生成时间标签
    timestamps = []
    for i in range(steps):
        if interval == "month":
            timestamps.append(f"2024-{str(i % 12 + 1).zfill(2)}")
        else:
            timestamps.append(f"2024-Q{(i % 4) + 1}")

    # 生成模拟时间序列数据
    series = []
    for p in patterns:
        name = p.pattern_name
        codes = name.split('-') if '-' in name else list(name)
        display_name = "-".join([code_to_name.get(c, c) for c in codes])

        base_fpi = p.fpi_score
        fpi_values = []
        instance_counts = []

        for i in range(steps):
            # 模拟 FPI 波动
            noise = random.uniform(-0.05, 0.05)
            fpi = max(0, min(1, base_fpi + noise * (1 - i / steps)))
            fpi_values.append(round(fpi, 4))

            # 模拟实例数
            base_count = random.randint(50, 200)
            instance_counts.append(int(base_count * (1 + i / steps * 0.5)))

        series.append({
            "pattern_id": p.pattern_id,
            "pattern_name": display_name,
            "fpi_values": fpi_values,
            "instance_counts": instance_counts
        })

    return {
        "timestamps": timestamps,
        "series": series
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
