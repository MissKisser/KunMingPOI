# __*__ coding=utf-8 __*__
# created by qyj @18.11.10

import psutil
import copy
import math
import itertools
import pandas as pd
import matplotlib.pyplot as plt

# ——————————————————————————————————————————————————————————————
# 定义产生实例索引到实例的映射
def genIntInstanceDic(instances):
    int_instanceDic = {}
    for i in range(len(instances)):
        int_instanceDic[i] = instances[i]
    return int_instanceDic

def genEvent_InstanceDic(instances):
    # 2026年1月18日增加代码，创建一个字典Event_instanceMap
    Event_instanceDic = {}
    for i in range(len(instances)):
        event = instances[i][1]
        if event in Event_instanceDic.keys():
            Event_instanceDic[event].add(instances[i])
        else:
            Event_instanceDic[event] = {instances[i]}
    return Event_instanceDic

def genInstanceIntDic(int_instanceDic):
    return {b: a for a, b in int_instanceDic.items()}

def mapIntToInstance(instanceIndex, int_instanceDic):
    return int_instanceDic.get(instanceIndex)

def mapInstanceToInt(instance, instance_intDic):
    return instance_intDic.get(instance)

# ——————————————————————————————————————————————————————————————
# 查看内存的函数(单位为M）
def checkConsumMemmory():
    info = psutil.virtual_memory()
    total_memmory = info.total
    free_memmory = info.free
    consum_memmory = (total_memmory - free_memmory) / (1024 * 1024)
    return consum_memmory
# ——————————————————————————————————————————————————————————————

# ——————————————————————————————————————————————————————————————
# 从文件读取实例
def getInstancesFromFile(file_path, grid_width):
    # 读取文件获得所有实例
    instances = []
    eventCount = {}
    with open(file_path, 'r') as file:
        instancesIndex = 0
        for line in file:
            if (instancesIndex < 3):
                instancesIndex += 1
                continue
            instance = line.split("\t")
            instances.append(tuple([int(float(instance[0])), instance[1], int(float(instance[2]) / grid_width) + 1,
                                    int(float(instance[3].replace("\n", "")) / grid_width) + 1, float(instance[2]),
                                    float(instance[3])]))
            eventCount[instance[1]] = eventCount.get(instance[1], 0) + 1
            instancesIndex += 1
        file.close()
    return instances, eventCount
# ——————————————————————————————————————————————————————————————

def calcDistance(curInstance_f_cd, comparedInstance_f_cd):
    distance = math.sqrt(math.pow((curInstance_f_cd[4] - comparedInstance_f_cd[4]), 2) + math.pow(
        (curInstance_f_cd[5] - comparedInstance_f_cd[5]), 2))
    distance = round(distance,4)
    return distance

#计算一个字符串的所有子集
def getAllSubset(str):
    if str == None or len(str) < 1:
        print("参数不合理！")
        return None
    arr = []
    arr.append(str[0:1])  # str首元素    单个元素的不是候选模式
    #print("当前子串为：", str[0:2])
    i = 1
    while i < len(str):
        lens = len(arr)
        j = 0
        while j < lens:
            arr.append(arr[j] + str[i])
            #print("当前子串为：",arr[j] + str[i])
            j += 1
        arr.append(str[i:i + 1])
        i += 1
    return arr


# 获得邻居返回idInstanceMap instanceIdMap及starNei,根据情况调用不同的距离函数：0:KDE  1：经典JoinLess，2：fuzzy_joinless
# idInstanceMap:{id:(innerId,type,x,y)}
# instanceIdMap:{(innderId, type, x, y):id}
# starNei: {id:[(id,memValue),(id,memValue)]}
# 2025.8.25 此版本求邻居是将邻居关系进行重复存储，因为每个实例都可能是星型模型的中心实例
def getStarNei(filePath,absolutDistance, distanceThreshold, wThreshold_f_gsn,disfuncType):
    instances_f_gsn, eventCount_f_gsn = getInstancesFromFile(filePath,distanceThreshold)

    print("载入实例的个数为",len(instances_f_gsn))
    intInstanceMap_f_gsn = genIntInstanceDic(instances_f_gsn)
    instance_int_map_f_gsn = genInstanceIntDic(intInstanceMap_f_gsn)
    Event_instanceMap = genEvent_InstanceDic(instances_f_gsn)
    grid_instances_dic = {}
    patternInstanceDisMap_f_gsn = {}
    for instance in instances_f_gsn:
        grid_position = tuple([instance[2], instance[3]])
        if (grid_instances_dic.keys().__contains__(grid_position)):
            instances_list = grid_instances_dic[grid_position]
            instances_list.append(instance)
            grid_instances_dic[grid_position] = instances_list
        else:
            grid_instances_dic[grid_position] = [instance]

    # 通过网格计算邻居
    centerInstanceIndex_neiInstanceIndex_memValueMap = {}
    for grid_position in grid_instances_dic.keys():
        if (grid_instances_dic.keys().__contains__(grid_position)):
            for cur_instance in grid_instances_dic.get(grid_position):
                # 遍历当前单元格的上方，右上方，当前单元格，右侧单元格，以及右下单元格5个单元格以获得邻居
                # 遍历上方单元格中的实例
                compared_grid_position = (grid_position[0], grid_position[1] + 1)
                if (grid_instances_dic.keys().__contains__(compared_grid_position)):
                    for compared_instance in grid_instances_dic.get(compared_grid_position):
                        if(disfuncType ==0):
                            memValue, distance = getInstancePairW(cur_instance,compared_instance,distanceThreshold)
                        if(disfuncType == 1):
                            memValue = calcDistance(cur_instance,compared_instance)
                            distance = memValue
                        if(disfuncType ==2):
                            memValue,distance = calcMemValue(cur_instance,compared_instance,absolutDistance,distanceThreshold)
                        if (((disfuncType == 1) and memValue < wThreshold_f_gsn) or ((disfuncType == 2) and (memValue > wThreshold_f_gsn))
                            or ((disfuncType ==0) and distance < wThreshold_f_gsn)):
                            if (cur_instance[1] != compared_instance[1]):
                                # if (cur_instance[1] < compared_instance[1]): 将compared_instance作为cur_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(cur_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(compared_instance)):
                                    curPattern_f_gsn = cur_instance[1] + compared_instance[1]
                                    #生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn,{})
                                    instanceDisMap_f_gsn[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] =min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(cur_instance, instance_int_map_f_gsn),distanceThreshold + 20),distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                                # elif (cur_instance[1] > compared_instance[1]) 将cur_instance作为compared_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(cur_instance)):
                                    curPattern_f_gsn =  compared_instance[1] +cur_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(compared_instance,
                                                         instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                # 遍历右上方单元格中的实例
                compared_grid_position = (grid_position[0] + 1, grid_position[1] + 1)
                if (grid_instances_dic.keys().__contains__(compared_grid_position)):
                    for compared_instance in grid_instances_dic.get(compared_grid_position):
                        if (disfuncType == 0):
                            memValue,distance = getInstancePairW(cur_instance, compared_instance, distanceThreshold)
                        if (disfuncType == 1):
                            memValue = calcDistance(cur_instance, compared_instance)
                            distance = memValue
                        if (disfuncType == 2):
                            memValue, distance = calcMemValue(cur_instance, compared_instance, absolutDistance,
                                                              distanceThreshold)
                        if (((disfuncType == 1) and memValue < wThreshold_f_gsn) or (
                                    (disfuncType == 2) and (memValue > wThreshold_f_gsn))
                                    or ((disfuncType == 0) and distance < wThreshold_f_gsn)):
                            if (cur_instance[1] != compared_instance[1]):
                                # if (cur_instance[1] < compared_instance[1]): 将compared_instance作为cur_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(cur_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(compared_instance)):
                                    curPattern_f_gsn =  cur_instance[1] + compared_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(cur_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                                # if (cur_instance[1] > compared_instance[1]): 将cur_instance作为compared_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(compared_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(cur_instance)):
                                    curPattern_f_gsn = compared_instance[1] + cur_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(compared_instance,
                                                         instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                # 遍历本单元格内的实例
                compared_grid_position = (grid_position[0], grid_position[1])
                if (grid_instances_dic.keys().__contains__(compared_grid_position)):
                    for compared_instance in grid_instances_dic.get(compared_grid_position):
                        if (disfuncType == 0):
                            memValue,distance = getInstancePairW(cur_instance, compared_instance, distanceThreshold)
                        if (disfuncType == 1):
                            memValue = calcDistance(cur_instance, compared_instance)
                            distance = memValue
                        if (disfuncType == 2):
                            memValue, distance = calcMemValue(cur_instance, compared_instance, absolutDistance,
                                                              distanceThreshold)
                        if (((disfuncType == 1) and memValue < wThreshold_f_gsn) or (
                                    (disfuncType == 2) and (memValue > wThreshold_f_gsn))
                                    or ((disfuncType == 0) and distance < wThreshold_f_gsn)):
                            if (cur_instance[1] !=  compared_instance[1]):
                                # if (cur_instance[1] < compared_instance[1]): 将compared_instance作为cur_instance的邻居
                                curPattern_f_gsn =  cur_instance[1] + compared_instance[1]
                                # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                instanceDisMap_f_gsn[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = min(
                                    instanceDisMap_f_gsn.get(mapInstanceToInt(cur_instance, instance_int_map_f_gsn), distanceThreshold + 20),
                                    distance)
                                patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(cur_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(compared_instance)):
                                    neiInstanceIndex_memValueMap[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                                # if (cur_instance[1] > compared_instance[1]): 将cur_instance作为compared_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(compared_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(cur_instance)):
                                    curPattern_f_gsn = compared_instance[1] + cur_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(compared_instance,
                                                         instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                # 遍历右侧单元格中的实例
                compared_grid_position = (grid_position[0] + 1, grid_position[1])
                if (grid_instances_dic.keys().__contains__(compared_grid_position)):
                    for compared_instance in grid_instances_dic.get(compared_grid_position):
                        if (disfuncType == 0):
                            memValue,distance = getInstancePairW(cur_instance, compared_instance, distanceThreshold)
                        if (disfuncType == 1):
                            memValue = calcDistance(cur_instance, compared_instance)
                            distance = memValue
                        if (disfuncType == 2):
                            memValue, distance = calcMemValue(cur_instance, compared_instance, absolutDistance,
                                                              distanceThreshold)
                        if (((disfuncType == 1) and memValue < wThreshold_f_gsn) or (
                                    (disfuncType == 2) and (memValue > wThreshold_f_gsn))
                                    or ((disfuncType == 0) and distance < wThreshold_f_gsn)):
                            if (cur_instance[1] !=  compared_instance[1]):
                                # if (cur_instance[1] < compared_instance[1]): 将compared_instance作为cur_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(cur_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(compared_instance)):
                                    curPattern_f_gsn = cur_instance[1] + compared_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(cur_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                                # if (cur_instance[1] > compared_instance[1]): 将cur_instance作为compared_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(compared_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(cur_instance)):
                                    curPattern_f_gsn = compared_instance[1] + cur_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(compared_instance,instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                #遍历右下侧单元格中的实例
                compared_grid_position = (grid_position[0] + 1, grid_position[1] - 1)
                if (grid_instances_dic.keys().__contains__(compared_grid_position)):
                    for compared_instance in grid_instances_dic.get(compared_grid_position):
                        if (disfuncType == 0):
                            memValue,distance = getInstancePairW(cur_instance, compared_instance, distanceThreshold)
                        if (disfuncType == 1):
                            memValue = calcDistance(cur_instance, compared_instance)
                            distance = memValue
                        if (disfuncType == 2):
                            memValue, distance = calcMemValue(cur_instance, compared_instance, absolutDistance,
                                                              distanceThreshold)
                        if (((disfuncType == 1) and memValue < wThreshold_f_gsn) or (
                                (disfuncType == 2) and (memValue > wThreshold_f_gsn))
                                or ((disfuncType == 0) and distance < wThreshold_f_gsn)):
                            if (cur_instance[1] != compared_instance[1]):
                                # if (cur_instance[1] < compared_instance[1]): 将compared_instance作为cur_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(cur_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(compared_instance)):
                                    curPattern_f_gsn = cur_instance[1] + compared_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(cur_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20),  distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(cur_instance, instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
                                # if (cur_instance[1] > compared_instance[1]): 将cur_instance作为compared_instance的邻居
                                neiInstanceIndex_memValueMap = centerInstanceIndex_neiInstanceIndex_memValueMap.get(
                                    mapInstanceToInt(compared_instance, instance_int_map_f_gsn), {})
                                if(not neiInstanceIndex_memValueMap.__contains__(cur_instance)):
                                    curPattern_f_gsn = compared_instance[1] + cur_instance[1]
                                    # 生成模式内第二个实例patternInstanceDisMap {pattern:{instance:dis}}
                                    instanceDisMap_f_gsn = patternInstanceDisMap_f_gsn.get(curPattern_f_gsn, {})
                                    instanceDisMap_f_gsn[mapInstanceToInt(compared_instance, instance_int_map_f_gsn)] = min(
                                        instanceDisMap_f_gsn.get(mapInstanceToInt(compared_instance, instance_int_map_f_gsn),
                                                                 distanceThreshold + 20), distance)
                                    patternInstanceDisMap_f_gsn[curPattern_f_gsn] = instanceDisMap_f_gsn

                                    neiInstanceIndex_memValueMap[mapInstanceToInt(cur_instance, instance_int_map_f_gsn)]= memValue
                                    centerInstanceIndex_neiInstanceIndex_memValueMap[
                                        mapInstanceToInt(compared_instance,
                                                         instance_int_map_f_gsn)] = neiInstanceIndex_memValueMap
    print("星型邻居的个数为：", len(centerInstanceIndex_neiInstanceIndex_memValueMap))
    return intInstanceMap_f_gsn, instance_int_map_f_gsn, eventCount_f_gsn, Event_instanceMap, centerInstanceIndex_neiInstanceIndex_memValueMap,patternInstanceDisMap_f_gsn

#生成表实例
def genTableInstance(patternStarInstanceDic_f_gti,centerIndex_neiIndex_memValueMap_f_gti):
    patternTableInstance_f_gti = {}
    for pattern_f_gti in patternStarInstanceDic_f_gti: #遍历星型实例表中的所有模式
        for rowInstance_f_gti in patternStarInstanceDic_f_gti[pattern_f_gti]: #遍历该模式下的所有行实例
            cliqueFlag = True
            for instance_f_gti in rowInstance_f_gti: #检查行实例每个实例是否与其他实例之间存在团关系
                for innerInstance_f_gti in rowInstance_f_gti:
                    if(instance_f_gti >innerInstance_f_gti):
                        if(innerInstance_f_gti not in centerIndex_neiIndex_memValueMap_f_gti.keys()):
                            cliqueFlag = False
                            break
                        if(instance_f_gti not in centerIndex_neiIndex_memValueMap_f_gti[innerInstance_f_gti].keys()):
                            cliqueFlag = False
                    if(instance_f_gti <innerInstance_f_gti):
                        if (instance_f_gti not in centerIndex_neiIndex_memValueMap_f_gti.keys()):
                            cliqueFlag = False
                            break
                        if (innerInstance_f_gti not in centerIndex_neiIndex_memValueMap_f_gti[instance_f_gti].keys()):
                            cliqueFlag = False
                    if cliqueFlag == False:
                        break
                if cliqueFlag == False:
                    break
            if(cliqueFlag == False):
                continue
            else:
                rowInstanceList_f_gti = patternTableInstance_f_gti.get(pattern_f_gti,[])
                rowInstanceList_f_gti.append(rowInstance_f_gti)
                patternTableInstance_f_gti[pattern_f_gti] = rowInstanceList_f_gti
    return patternTableInstance_f_gti

#计算FPI值
#输入：星型实例,fpi阈值,直接使用主程序中的idInstanceMap,InstanceIdMap
#输出：频繁模式及对应的fpi值 {pattern:tableInstance}
def calcFPI(patternStarInstance_f_cf, patternInsWSum_f_cf):
    #遍历所有模式，获得每个行实例中对应实例的紧密度，该行实例的紧密度存入rowCompactList中，所有对象对应的实例的紧密度存入
    #字典objInstanceCompMap即{obj:instance:compactValue}中
    patternFpi_f_cf = {}
    for pattern_f_cf in patternStarInstance_f_cf.keys():
        maxNumOfEventCount_f_cf = 0
        for i_f_cf in pattern_f_cf:
            maxNumOfEventCount_f_cf = max(maxNumOfEventCount_f_cf, eventCount[i_f_cf])
        patternFpi_f_cf[pattern_f_cf] = round(patternInsWSum_f_cf[pattern_f_cf]/pow(maxNumOfEventCount_f_cf,2),6)
    return patternFpi_f_cf

#生成二阶表实例
#输入：cnmMap_f_gl2ti 中心实例和邻居实例的字典
#输出： patternTableInstance:{pattern1:[(instanceIndex1,instanceIndex2), .......]
def genLevel2TableInstance(intInstanceMap_f_gl2ti, cnmMap_f_gl2ti):
    patternTableInstance_f_gl2ti = {}
    patternInsWSum_f_gl2ti = {}
    #遍历获取每个实例对对应模式，并将该实例对及其权重写入模式对应的字典中[pattern:{(instancePair):w
    for centerInstanceIndex_f_gl2ti in cnmMap_f_gl2ti.keys():
        centerInstance_f_gl2ti = intInstanceMap_f_gl2ti[centerInstanceIndex_f_gl2ti]
        for neiInstanceIndex_f_gl2ti in cnmMap_f_gl2ti[centerInstanceIndex_f_gl2ti]:
            neiInstance_f_gl2ti = intInstanceMap_f_gl2ti[neiInstanceIndex_f_gl2ti]
            pattern_f_gl2ti = centerInstance_f_gl2ti[1] + neiInstance_f_gl2ti[1] #获取实例对对应的模式
            rowInstance_f_gl2ti = (centerInstanceIndex_f_gl2ti, neiInstanceIndex_f_gl2ti)
            if(rowInstance_f_gl2ti not in patternTableInstance_f_gl2ti.values()):
                tempList_f_gl2ti = patternTableInstance_f_gl2ti.get(pattern_f_gl2ti,[])
                tempSum_f_gl2ti = patternInsWSum_f_gl2ti.get(pattern_f_gl2ti,0)
                tempSum_f_gl2ti += cnmMap_f_gl2ti[centerInstanceIndex_f_gl2ti][neiInstanceIndex_f_gl2ti]
                tempList_f_gl2ti.append(rowInstance_f_gl2ti)
                patternTableInstance_f_gl2ti[pattern_f_gl2ti] = tempList_f_gl2ti
                patternInsWSum_f_gl2ti[pattern_f_gl2ti] = tempSum_f_gl2ti
    #如果在tableInstance(未经过频繁性检验，应该称为星型实例）中存在重复元素进行去重处理
    #patternTableInstance_f_gl2ti = {k:list(set(v)) for k,v in patternTableInstance_f_gl2ti.items()}
    patternFpi_f_gl2ti = calcFPI(patternTableInstance_f_gl2ti, patternInsWSum_f_gl2ti)
    frePatternTableInstance_f_gl2ti = {k:patternTableInstance_f_gl2ti[k] for k,v in patternFpi_f_gl2ti.items()}
    return patternFpi_f_gl2ti,frePatternTableInstance_f_gl2ti
#获取两个实例之间的隶属度
#cnmMap_f_gmv是中心实例与所有邻居的隶属度字典
def getMemValue(instanceA_f_gmv, instanceB_f_gmv, cnmMap_f_gmv):
    return cnmMap_f_gmv[instanceA_f_gmv][instanceB_f_gmv]

class nodeTree:
    def __init__(self,id,memValue = 0.0):
        self.id = id
        self.parent = None
        self.memValue = memValue
        self.compactValue = 0.0
        self.children = {}

    def disp(self, idInstanceMap, ind = 1):
        print(" " * ind,idInstanceMap.get(self.id,-1),"  ",self.compactValue)
        for child in self.children.values():
            child.disp(idInstanceMap, ind + 1)

    def updateCompactValue(self):
        return None

#根据输入的子图创建树，树结构如下
#       -1,0.0
#   0,0.0    1,0.0
# 121,0.8      132,0.2
def createTree(subGraph_f_ct, insTable2_f_ct):
    rtTree_f_ct = nodeTree(-1)
    eventIndexInGraph_f_ct = 0
    while(eventIndexInGraph_f_ct < len(subGraph_f_ct)-1):
        if(eventIndexInGraph_f_ct == 1):
            eventIndexInGraph_f_ct += 1
            continue
        # 将当前模式对应的实例对加入生成树中
        # 获取当前模式
        curPattern_f_ct = subGraph_f_ct[eventIndexInGraph_f_ct] + subGraph_f_ct[eventIndexInGraph_f_ct+1]
        if eventIndexInGraph_f_ct == 0:
            curPattern_f_ct = subGraph_f_ct[0] + subGraph_f_ct[1]
            #如果当前模式为极大团中的第一对模式串，将模式对应的表实例插入生成树中
            for instancePair_f_ct in insTable2_f_ct[curPattern_f_ct]:
                #如果当前生成树包含实例对中的第一个节点，将第二个节点生成树节点插入第一个节点的子节点字典中
                # 否则直接插入节点对构成的树节点
                if(instancePair_f_ct[0] in rtTree_f_ct.children.keys()):
                    curNode_f_ct = rtTree_f_ct.children[instancePair_f_ct[0]]
                    curNode_f_ct.children[instancePair_f_ct[1]] = nodeTree(instancePair_f_ct[1])
                    curNode_f_ct.children[instancePair_f_ct[1]].parent = curNode_f_ct
                else:
                    curNode_f_ct = nodeTree(instancePair_f_ct[0])
                    curNode_f_ct.children[instancePair_f_ct[1]] = nodeTree(instancePair_f_ct[1])
                    curNode_f_ct.children[instancePair_f_ct[1]].parent = curNode_f_ct
                    rtTree_f_ct.children[instancePair_f_ct[0]] = curNode_f_ct
                    curNode_f_ct.parent = rtTree_f_ct
        else:
            #将后面的模式对应的节点插入生成树的后续节点中，并检查团关系
            #遍历获取当前层次的所有树节点
            stackIndex_f_ct = 0
            curLayerStack_f_ct = [rtTree_f_ct]
            while(stackIndex_f_ct < eventIndexInGraph_f_ct + 1):
                stack_f_ct = curLayerStack_f_ct
                curLayerStack_f_ct = []
                while(len(stack_f_ct) > 0):
                    popEle_f_ct = stack_f_ct.pop(0)
                    for child_f_ct in popEle_f_ct.children.values():
                        curLayerStack_f_ct.append(child_f_ct)
                stackIndex_f_ct += 1
            #遍历curpatttern_f_ct对应的所有实例对，如果实例与当前树节点一致，检查实例与祖先节点的邻居关系
            #如果都满足邻居关系则将该节点扩展为当前树节点的子节点，否则遍历下一个实例对
            for instancePair_f_ct in insTable2_f_ct[curPattern_f_ct]:
                #遍历当前子模式串对应的实例对，如果实例对中的第0个实例与当前层某个树节点中包含的实例相同：扩展该节点
                for treeNode_f_ct in curLayerStack_f_ct:
                    if(instancePair_f_ct[0] == treeNode_f_ct.id):
                        #检查第1个节点是否与该节点的祖先节点存在团关系，如果不存在，遍历该层中的下一个树节点break
                        curNode_f_ct = treeNode_f_ct
                        #定义变量逐层向上检查
                        flag_f_ct = eventIndexInGraph_f_ct -1 #从当前树节点的父节点开始检查邻居关系
                        while(flag_f_ct > 0):
                            if(instancePair_f_ct[1] in centerIndex_neiIndex_memValueMap[curNode_f_ct.parent.id].keys()):
                                curNode_f_ct = curNode_f_ct.parent
                                flag_f_ct -= 1
                            else:
                                break
                        #如果flag ==0 说明instancePair[1]与根节点也存在邻居关系，即与所有实例构成团关系
                        if(flag_f_ct == 0):
                            extendNode_f_ct = nodeTree(instancePair_f_ct[1])
                            extendNode_f_ct.parent = treeNode_f_ct
                            treeNode_f_ct.children[instancePair_f_ct[1]] = extendNode_f_ct
        eventIndexInGraph_f_ct += 1
    return rtTree_f_ct

#检测当前无向图的深度，（1）计算无向图图的深度，（2）如果深度满足条件计算FPI值，如果不满足条件将该无向图的子图放入队列中重复（1）
def getFrequentPattern(cliqueGraphList_f_gfp,patternTableInstance_f_gfp,idInstanceMap):
    frequnentCliqueList_f_gfp = []
    unFreqCliqueList_f_gfp = []
    #对当前团生成生成树
    while (len(cliqueGraphList_f_gfp) > 0):
        print(cliqueGraphList_f_gfp)
        clique_f_gfp = cliqueGraphList_f_gfp.pop(0)
        if(clique_f_gfp in unFreqCliqueList_f_gfp):
            continue
        #记录当前团中的每个实例对的累计
        rtTree_f_gfp = createTree(clique_f_gfp, patternTableInstance_f_gfp)
        insPairWdic_f_gfp = {}
        patternWdic_f_gfp = {}
        #遍历树找到当前层节点与其子节点的权重
        stackIndex_f_gfp = 0 #存储当前遍历的节点在无向图中的层次
        curLayerStack_f_gfp = list(rtTree_f_gfp.children.values())  #先获取rtTree的第一层所包含的所有子节点
        lastStack_f_gfp = copy.copy(curLayerStack_f_gfp) #lastStack保存当前遍历的最后一层的结果，在程序的下面代表被遍历
        # 当前层的上一层
        while (stackIndex_f_gfp < len(clique_f_gfp) and len(curLayerStack_f_gfp) >0): #遍历每一层，从第1层开始
            # 对当前层的所有节点的子节点遍历找到与枚举二阶子模式相符的事件的子实例
            for curNode_f_gfp in curLayerStack_f_gfp:
                innerLayerStack_f_gfp = list(curNode_f_gfp.children.values())
                innerLoopIndex_f_gfp = stackIndex_f_gfp + 1
                #将后面层的实例逐层进行遍历
                while (innerLoopIndex_f_gfp < len(clique_f_gfp)):  # 遍历每一层，从第1层开始
                    innerStack_f_gfp = copy.copy(innerLayerStack_f_gfp)
                    innerLayerStack_f_gfp = []
                    while (len(innerStack_f_gfp) > 0):
                        innerPopEle_f_gfp = innerStack_f_gfp.pop(0)
                        for innerChild_f_gfp in innerPopEle_f_gfp.children.values():
                            innerLayerStack_f_gfp.append(innerChild_f_gfp)
                    #如果当前遍历层节点个数为0，跳出循环遍历下一个节点
                    if(len(innerLayerStack_f_gfp) ==0):
                        break
                    else:
                        #将该层每个实例与当前节点的w值提取出来放入insPairWDic中
                        for loopNode_f_gfp in innerLayerStack_f_gfp:
                            if((curNode_f_gfp.id,loopNode_f_gfp.id) not in insPairWdic_f_gfp.keys()):
                                print("curNode",curNode_f_gfp.id,"loopNode",loopNode_f_gfp.id)
                                insPairWdic_f_gfp[(curNode_f_gfp.id,loopNode_f_gfp.id)] = \
                                    centerIndex_neiIndex_memValueMap[curNode_f_gfp.id][loopNode_f_gfp.id]
                    innerLoopIndex_f_gfp += 1

            stack_f_gfp = copy.copy(curLayerStack_f_gfp)
            lastStack_f_gfp = copy.copy(curLayerStack_f_gfp)
            curLayerStack_f_gfp = []
            while (len(stack_f_gfp) > 0):
                popEle_f_gfp = stack_f_gfp.pop(0)
                for child_f_gfp in popEle_f_gfp.children.values():
                    curLayerStack_f_gfp.append(child_f_gfp)
            stackIndex_f_gfp += 1

        #如果最后一层curLayerStar_f_gfp中的元素类型不为clique_f_gfp中最后一个元素则取该无向图的子图加入cliqueGraphList中
        if(len(curLayerStack_f_gfp) == 0):
            curLayerStack_f_gfp = lastStack_f_gfp
        if(idInstanceMap[curLayerStack_f_gfp[0].id][1] != clique_f_gfp[-1]):
            if(len(clique_f_gfp)>2):
            #获取clique_f_gfp的子模式
                subCliuqes_f_gfp = []
                for i in range(len(clique_f_gfp)):
                    cliqueCopy_f_gfp = copy.copy(clique_f_gfp)
                    cliqueCopy_f_gfp.pop(i)
                    #如果现有团列表中不存在当前团的超集，则将该团加入现有团列表中
                    appendFlag_f_gfp = True
                    for cliqueEle_f_gfp in cliqueGraphList_f_gfp:
                        if len([j for j in cliqueCopy_f_gfp if j in cliqueEle_f_gfp]) == len(cliqueCopy_f_gfp): #判断枚举团是否是现有团的超集
                            appendFlag_f_gfp = False
                    for cliqueEle_f_gfp in frequnentCliqueList_f_gfp:
                        if len([j for j in cliqueCopy_f_gfp if j in cliqueEle_f_gfp]) == len(cliqueCopy_f_gfp): #判断枚举团是否是现有团的超集
                            appendFlag_f_gfp = False
                    if(appendFlag_f_gfp == True):
                        subCliuqes_f_gfp.append(cliqueCopy_f_gfp)
                cliqueGraphList_f_gfp.extend(subCliuqes_f_gfp)

        else:
            # 将insPairW中的所有实例归入对应的模式中，并计算模式的权重。取最小的权重作为该团的参与度
            for insPair_f_gfp in insPairWdic_f_gfp.keys():
                patternOfPair_f_gfp = idInstanceMap[insPairWdic_f_gfp[0]][1] + idInstanceMap[insPairWdic_f_gfp[1]][1]
                patternWdic_f_gfp[patternOfPair_f_gfp] = patternWdic_f_gfp.get(patternOfPair_f_gfp,0) + insPairWdic_f_gfp[insPair_f_gfp]
            fpi_f_gfp = 1.0
            for patternLoop_f_gfp in patternWdic_f_gfp.keys():
                maxNumOfEvent_f_gfp = max(eventCount[patternLoop_f_gfp[0],patternLoop_f_gfp[1]])
                fpi_f_gfp = min(fpi_f_gfp,patternWdic_f_gfp[patternLoop_f_gfp]/maxNumOfEvent_f_gfp)
            #如果当期团的fpi小于FPI阈值，则取其子模式进行扩展
            if(fpi_f_gfp < fpiThreshold):
                subCliuqes_f_gfp = []
                for i in range(len(clique_f_gfp)):
                    cliqueCopy_f_gfp = copy.copy(clique_f_gfp)
                    cliqueCopy_f_gfp.pop(i)
                    # 如果现有团列表中不存在当前团的超集，则将该团加入现有团列表中
                    appendFlag_f_gfp = True
                    for cliqueEle_f_gfp in cliqueGraphList_f_gfp:
                        if len([j for j in cliqueCopy_f_gfp if j in cliqueEle_f_gfp]) == len(cliqueCopy_f_gfp): #判断枚举团是否是现有团的超集
                            appendFlag_f_gfp = False
                    for cliqueEle_f_gfp in frequnentCliqueList_f_gfp:
                        if len([j for j in cliqueCopy_f_gfp if j in cliqueEle_f_gfp]) == len(cliqueCopy_f_gfp): #判断枚举团是否是现有团的超集
                            appendFlag_f_gfp = False
                    if cliqueCopy_f_gfp in unFreqCliqueList_f_gfp:
                        appendFlag_f_gfp = False
                    if (appendFlag_f_gfp == True):
                        subCliuqes_f_gfp.append(cliqueCopy_f_gfp)
                cliqueGraphList_f_gfp.extend(subCliuqes_f_gfp)
                unFreqCliqueList_f_gfp.append(clique_f_gfp)
            else:
                frequnentCliqueList_f_gfp.append(clique_f_gfp)
        print("频繁模式为：",sorted(frequnentCliqueList_f_gfp))
    return frequnentCliqueList_f_gfp

#生成2阶表实例
def getLevel2FreqentPattern(patternTableInstance_f_gl2fp):
    frequentPatterns_f_gl2fp = []
    patternFpiDic_f_gl2fp = {}
    for pattern_f_gl2fp in patternTableInstance_f_gl2fp.keys():
        eventInstanceSetDic_f_gl2fp = {}
        for rowInstance_f_gl2fp in patternTableInstance_f_gl2fp[pattern_f_gl2fp]:
            if(eventInstanceSetDic_f_gl2fp.get(pattern_f_gl2fp[0],0) == 0):
                eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[0]] = {rowInstance_f_gl2fp[0]}
                eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[1]] = {rowInstance_f_gl2fp[1]}
            else:
                event1InstanceSet_f_gl2fp = eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[0]]
                event1InstanceSet_f_gl2fp.add(rowInstance_f_gl2fp[0])
                eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[0]] = event1InstanceSet_f_gl2fp
                event2InstanceSet_f_gl2fp = eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[1]]
                event2InstanceSet_f_gl2fp.add(rowInstance_f_gl2fp[1])
                eventInstanceSetDic_f_gl2fp[pattern_f_gl2fp[1]] = event2InstanceSet_f_gl2fp
        fpi_f_gl2fp = 1.0
        for event_f_gl2fp in pattern_f_gl2fp:
            eventNum_f_gl2fp = len(eventInstanceSetDic_f_gl2fp[event_f_gl2fp])
            eventCount_f_gl2fp = eventCount[event_f_gl2fp]
            fpi_f_gl2fp = min(fpi_f_gl2fp, float(eventNum_f_gl2fp)/eventCount_f_gl2fp)
        frequentPatterns_f_gl2fp.append(pattern_f_gl2fp)
        patternFpiDic_f_gl2fp[pattern_f_gl2fp] = round(fpi_f_gl2fp,4)
    return sorted(frequentPatterns_f_gl2fp),patternFpiDic_f_gl2fp

#KED算法扩充
#获得两个实例之间的距离
def getInstancePairW(instanceA_f_gipw, instanceB_f_gipw, distanceThreshold):
    #获取两个实例类别对应出现次数的最大值
    w_f_gipw = math.pow(math.e,-(pow(calcDistance(instanceA_f_gipw,instanceB_f_gipw),2)
                                 /(2*pow(distanceThreshold,2))))
    distance_f_gipw = calcDistance(instanceA_f_gipw,instanceB_f_gipw)
    return  w_f_gipw, distance_f_gipw

#获得两个实例之间的隶属度
def calcMemValue(curInstance_f_cmv, comparedInstance_f_cmv, abosult_distance, distance_threshold):
    distance = math.sqrt(math.pow(curInstance_f_cmv[4] - comparedInstance_f_cmv[4], 2) + math.pow(
        curInstance_f_cmv[5] - comparedInstance_f_cmv[5], 2))
    distance_f_cmv = round(distance,4)

    if (distance_f_cmv < abosult_distance):
        memValue_f_cmv = 1.0
    elif (distance_f_cmv > distance_threshold):
        memValue_f_cmv = 0.0
    else:
        memValue_f_cmv = 1 - math.pow((distance_f_cmv - abosult_distance),2) / math.pow((distance_threshold - abosult_distance),2)
    return round(memValue_f_cmv, 4),distance_f_cmv

#将得到的PI值放入0-1 0.05为间距的间隔中
def getIntervalData(piValues_f_gid,interVal_f_gid):
    divideValue_f_gid = 1/interVal_f_gid
    newPatternFPiMap_f_gid = {}
    interValList_f_gid = []
    for piValue_f_gid in piValues_f_gid.items():
        formatData_f_gid = round(piValue_f_gid[1]*divideValue_f_gid)/float(divideValue_f_gid)
        interValList_f_gid.append(formatData_f_gid)
        newPatternFPiMap_f_gid[piValue_f_gid[0]] = formatData_f_gid
    piValues_f_gid = newPatternFPiMap_f_gid
    return interValList_f_gid,piValues_f_gid

#获得每个数字出现的频率
def getFreq(valuesList_f_gf,eventCount_f_gf, patternPiMap_f_gf):
    valueFreqMap_f_gf = {}
    valueFreqFloat_f_gf = {}
    for value_f_gf in valuesList_f_gf:
        freq_f_gf = valueFreqMap_f_gf.get(value_f_gf,0)
        freq_f_gf += 1
        valueFreqMap_f_gf[value_f_gf] = freq_f_gf
    valueFreqMap_f_gf[0] = (len(eventCount_f_gf) *(len(eventCount_f_gf) -1))/2 - len(valuesList_f_gf)
    for value_f_gf in valueFreqMap_f_gf.keys():
        valueFreqFloat_f_gf[value_f_gf] = 2*float(valueFreqMap_f_gf[value_f_gf])/(len(eventCount_f_gf) *(len(eventCount_f_gf) -1))
    uniquePatterns = []
    for i_f_gf in patternPiMap_f_gf.items():
        if(valueFreqMap_f_gf[i_f_gf[1]] ==1):
            uniquePatterns.append(i_f_gf[0])
    print("只出现一次的模式有：",len(uniquePatterns),sorted(uniquePatterns))
    print(valueFreqMap_f_gf)
    return valueFreqFloat_f_gf
#使用二阶表实例建立无向图
#输出：无向图列表UDGlist:[udgSubGraph1, udgSubGraph2, .......]

#给定xList, yList, title,xLabel,yLabel,legend ,barInter(条状大小）画出条状图
def drawBar(barInter_f_db, xList_f_db, yList_f_db, title_f_db, xLabel_f_db, yLabel_f_db, legendContent_f_db):
    plt.bar(xList_f_db, yList_f_db, width=barInter_f_db, facecolor='yellowgreen', edgecolor='white')
    plt.xticks()
    # 图例
    plt.legend([legendContent_f_db])
    # 设置x轴范围值
    plt.xlim([min(xList_f_db), max(xList_f_db)])
    # 设置x轴标签
    plt.xlabel(xLabel_f_db)
    # 设置y轴标签
    plt.ylabel(yLabel_f_db)
    plt.title(title_f_db)
    plt.show()

if __name__ == "__main__":
    fpiThreshold = 0.00001
    distanceThreshold = 150
    wThreshold = 0.5

    #生成邻居列表
    idInstanceMap, instanceIdMap, eventCount, centerIndex_neiIndex_memValueMap ,patternDisMap= getStarNei("d:\\data\\real.data",20,distanceThreshold,distanceThreshold,0)
    #生成二阶表实例
    patternPiMap, patternTableInstance = genLevel2TableInstance(idInstanceMap,centerIndex_neiIndex_memValueMap)
    patternFpiPairList = list(patternPiMap.items())
    patternFpiPairList.sort(key=lambda i: i[1], reverse=True)
    print("模式对应的参与度为", patternFpiPairList)
    # 将模式对应的FPI存入CSV文件中
    patternFpiDf = pd.DataFrame(patternFpiPairList)
    patternFpiDf.to_csv("MaximCliquePatternPi.csv")
    #level2FreqPatterns,patternFpiMap = getLevel2FreqentPattern(patternTableInstance)  #该函数错误，待查
    barInter = 0.0000004
    interValues,patternPiMap = getIntervalData(patternPiMap, barInter)
    # 将频率按pi值大小排序后存入表中
    valueFreqMap = getFreq(interValues,eventCount, patternPiMap)
    valueFreqPair = list(valueFreqMap.items())
    valueFreqPair.sort(key=lambda i: i[0])
    patternFpiDf = pd.DataFrame(valueFreqPair)
    patternFpiDf.to_csv("MaximCliquePiFreq.csv")
    print(u"模式对应的频率为：", valueFreqPair)
    x = [i[0] for i in valueFreqPair]
    y = [i[1] for i in valueFreqPair]
    print(x, y)
    plt.bar(x, y, width=barInter, facecolor='yellowgreen', edgecolor='white')
    plt.xticks()
    # 图例
    plt.legend(["the frequency of PI_K"])
    # 设置x轴范围值
    plt.xlim([0, max(x)])
    # 设置x轴标签
    plt.xlabel("PI_K")
    # 设置y轴标签
    plt.ylabel("Frequency")
    #plt.title("maximClique")
    plt.show()


#FPI_jionless使用
#根据团实例计算给定模式的fpi值
#获取compcValue列表
# 计算模式的紧密度：对每个行实例，取当前实例与其他实例隶属度的最小值作为
def getCompactValue(rowInstance_f_gcv,centerIndex_neiIndex_memValueMap_f_gcv):
    cliqueFlag_f_gcv = True  #判断当前行实例是否为团
    # 返回值为rowInstance内部每个实例在行实例中的紧密度值列表
    compactValueList_f_gcv = []
    level_f_gcv = len(rowInstance_f_gcv)
    outInstanceIndex_f_gcv = 0
    while (outInstanceIndex_f_gcv < level_f_gcv):
        curInstanceIndex_f_gcv = rowInstance_f_gcv[outInstanceIndex_f_gcv]
        compactValue_f_gcv = 1.0
        inInstanceIndex_f_gcv = 0
        while (inInstanceIndex_f_gcv < level_f_gcv):
            comparedInstanceIndex_f_gcv = rowInstance_f_gcv[inInstanceIndex_f_gcv]
            if (outInstanceIndex_f_gcv < inInstanceIndex_f_gcv):  #当当前实例的id小于被比较实例的id时
                if(curInstanceIndex_f_gcv not in centerIndex_neiIndex_memValueMap_f_gcv.keys()):  #如果行实例中紧密度的生成过程中，左侧实例没有邻居，则证明左侧实例的邻居中不可能包含其后被比较的其他实例，所以无法构成团
                    cliqueFlag_f_gcv = False
                    break
                neiIndexMemValueMap_f_gcv = centerIndex_neiIndex_memValueMap_f_gcv[curInstanceIndex_f_gcv]
                if(comparedInstanceIndex_f_gcv not in neiIndexMemValueMap_f_gcv.keys()): #如果左侧实例的邻居列表中不包含被比较实例同样不能构成团
                    cliqueFlag_f_gcv = False
                    break
                compactValue_f_gcv = min(compactValue_f_gcv, neiIndexMemValueMap_f_gcv[comparedInstanceIndex_f_gcv])
            elif (outInstanceIndex_f_gcv > inInstanceIndex_f_gcv):
                if (comparedInstanceIndex_f_gcv not in centerIndex_neiIndex_memValueMap_f_gcv.keys()):
                    cliqueFlag_f_gcv = False
                    break
                if (curInstanceIndex_f_gcv not in centerIndex_neiIndex_memValueMap_f_gcv[comparedInstanceIndex_f_gcv].keys()):
                    cliqueFlag_f_gcv = False
                    break
                compactValue_f_gcv = min(compactValue_f_gcv,
                                   centerIndex_neiIndex_memValueMap_f_gcv[comparedInstanceIndex_f_gcv][curInstanceIndex_f_gcv])
            inInstanceIndex_f_gcv += 1
        if(cliqueFlag_f_gcv == False):
            break
        compactValueList_f_gcv.append(compactValue_f_gcv)
        outInstanceIndex_f_gcv += 1
    return cliqueFlag_f_gcv, compactValueList_f_gcv

def calcFPIforPattern(cliquesInstance_f_cfp, pattern_f_cfp,centerIndex_neiIndex_memValueMap_f_cfp,eventCount_f_cfp):
    event_instance_compactMap_f_gfp = {}
    for rowInstance_f_gfp in cliquesInstance_f_cfp:  # 获取当前模式所对应的行实例
        cliqueFlag_f_gfp, compactValueList_f_gfp = getCompactValue(rowInstance_f_gfp,centerIndex_neiIndex_memValueMap_f_cfp)  # 获取当前行实例的紧密度列表
        if (cliqueFlag_f_gfp == False):  # 如果当前行实例不为团则计算下一个行实例
            continue

        # 遍历行实例内的每个实例将其紧密度存入每个事件对应的实例字典中event_instance_compactMap_f_gfp即{event:{instance:maxcompactvalue}}
        level_f_gfp = len(pattern_f_cfp)
        instanceIndex = 0
        while (instanceIndex < level_f_gfp):  # 遍历行实例
            # 获取当前事件对应的实例紧密度字典，如为空则返回空字典
            instance_compactMap_f_gfp = event_instance_compactMap_f_gfp.get(pattern_f_cfp[instanceIndex], {})
            # 获取当前实例的紧密度值在字典中存储的紧密度值，如果字典中还没有当前实例的紧密度值则返回空
            compactValue_f_gfp = instance_compactMap_f_gfp.get(rowInstance_f_gfp[instanceIndex], 0)
            # 比较当前实例与字典中已存储实例的紧密度值，返回最大的以更新该实例的紧密度值
            instance_compactMap_f_gfp[rowInstance_f_gfp[instanceIndex]] = max(compactValue_f_gfp,
                                                                              compactValueList_f_gfp[instanceIndex])
            # 更新当前事件对应的实例紧密度字典
            event_instance_compactMap_f_gfp[pattern_f_cfp[instanceIndex]] = instance_compactMap_f_gfp
            instanceIndex += 1
    # 如果该模式中不存在表实例则不计算模糊参与度
    fpi = 1.0

    for event in pattern_f_cfp:
        if (event not in event_instance_compactMap_f_gfp.keys()):
            fpi = 0.0
            break
        if pattern_f_cfp == "HJK":
            print(pattern_f_cfp)
        eventCompactSum = sum(event_instance_compactMap_f_gfp[event].values())
        curEventCount = eventCount_f_cfp[event]
        fpi = min(fpi, eventCompactSum / curEventCount)
        fpi = round(fpi, 4)
        return fpi
#-------------------------------------------------------------------------------------------------
#FSS树
class CInsTree():

    def __init__(self, instance=None, parent =None):
        self.instance = instance  #使用ID存储当前节点的实例内容
        self.parent = parent #CInstance类型，值唯一
#-----------------------------------------------------------------------

#根据输入的模式构建树
def createPatternTree(patternInput_f_cpt, eventInstanceDic_f_cpt,centerIndexEventNeiIndexMap_f_cpt):

    cursor_f_cpt = 0
    cliques_f_cpt = []
    patternLevel_f_cpt = len(patternInput_f_cpt)
    childNodeList_f_cpt = []
    while cursor_f_cpt < patternLevel_f_cpt - 1:
        #当cursor_f_cpt为0即第一层创建时，
        # 遍历模式第一个事件所对应的所有，以该实例i_loop_f_cpt创建树节点，节点的父节点为None为根节点；
        # 遍历该实例i_loop_f_cpt的所有邻居节点，以邻居节点i_loop2_f_cpt创建树节点，节点的父节点为i_loop_f_cpt对应的树节点，
        # 并将i_loop2_f_cpt对应的树节点加入子节点列表childNodeList_f_cpt为下一节遍历提供数据来源。
        if cursor_f_cpt == 0:
            cm2_f_cpt = patternInput_f_cpt[:2]
            instanceList_f_cpt = eventInstanceDic_f_cpt[cm2_f_cpt[0]]

            for i_loop_f_cpt in instanceList_f_cpt:
                if i_loop_f_cpt not in centerIndexEventNeiIndexMap_f_cpt.keys():
                    continue
                if cm2_f_cpt[1] not in centerIndexEventNeiIndexMap_f_cpt[i_loop_f_cpt].keys():
                    continue
                curNode_f_cpt = CInsTree(i_loop_f_cpt,None)
                for i_loop2_f_cpt in centerIndexEventNeiIndexMap_f_cpt[i_loop_f_cpt][cm2_f_cpt[1]]:
                    childNode_f_cpt = CInsTree(i_loop2_f_cpt, curNode_f_cpt)
                    childNodeList_f_cpt.append(childNode_f_cpt)

            cursor_f_cpt = cursor_f_cpt + 1
        else:
            curChildNodelist_f_cpt = []
            for i_loop_f_cpt in childNodeList_f_cpt: #遍历树的上一层的所有节点
                #遍历树上一层节点对应本层事件的所有邻居
                if i_loop_f_cpt.instance not in centerIndexEventNeiIndexMap_f_cpt.keys():
                    continue
                if patternInput_f_cpt[cursor_f_cpt + 1] not in centerIndexEventNeiIndexMap_f_cpt[i_loop_f_cpt.instance].keys():
                    continue
                if centerIndexEventNeiIndexMap_f_cpt[i_loop_f_cpt.instance][patternInput_f_cpt[cursor_f_cpt +1]] == None:
                    continue
                for i_loop2_f_cpt in centerIndexEventNeiIndexMap_f_cpt[i_loop_f_cpt.instance][patternInput_f_cpt[cursor_f_cpt +1]]:
                    #判断当前节点是否与父节点以上的所有节点都存在邻居关系，如果都存在则将团实例存储在列表中
                    compareNode_f_cpt = i_loop_f_cpt.parent

                    clique_flag_f_cpt = 1
                    for i_loop3_f_cpt in range(cursor_f_cpt):
                        if compareNode_f_cpt.instance not in centerIndexEventNeiIndexMap_f_cpt.keys():
                            clique_flag_f_cpt = 0
                            break
                        if patternInput_f_cpt[cursor_f_cpt +1] not in centerIndexEventNeiIndexMap_f_cpt[compareNode_f_cpt.instance].keys():
                            clique_flag_f_cpt = 0
                            break
                        if i_loop2_f_cpt not in centerIndexEventNeiIndexMap_f_cpt[compareNode_f_cpt.instance][patternInput_f_cpt[cursor_f_cpt +1]]:
                            clique_flag_f_cpt = 0
                            break
                        compareNode_f_cpt = compareNode_f_cpt.parent

                    if clique_flag_f_cpt == 0:
                        continue
                    else:
                        childNode_f_cpt = CInsTree(i_loop2_f_cpt, i_loop_f_cpt)
                        curChildNodelist_f_cpt.append(childNode_f_cpt)
                        if cursor_f_cpt == patternLevel_f_cpt -2: #树的层数为pattern-1时，从0到pattern-1
                            cliqueElements_f_cpt = [i_loop_f_cpt.instance,i_loop2_f_cpt] #从最底层收集构成团的行实例
                            cliqueElementNode_f_cpt = i_loop_f_cpt.parent #父节点的父亲节点被作为下一次比较的对象
                            while cliqueElementNode_f_cpt != None: #直至父节点为None，即从叶节点遍历到根节点（根节点的父节点为None）
                                cliqueElements_f_cpt.insert(0,cliqueElementNode_f_cpt.instance)
                                cliqueElementNode_f_cpt = cliqueElementNode_f_cpt.parent

                            cliques_f_cpt.append(cliqueElements_f_cpt)
            cursor_f_cpt = cursor_f_cpt + 1
            childNodeList_f_cpt = curChildNodelist_f_cpt
    return cliques_f_cpt

#FSS算法使用
#根据团实例计算给定模式的fpi值
#获取compcValue列表
# 计算模式的紧密度：对每个行实例，取当前实例与其他实例隶属度的最小值作为
def getTreeCompactValue(rowInstance_f_gtcv,centerIndex_neiIndex_memValueMap_f_gtcv):
    # 返回值为rowInstance内部每个实例在行实例中的紧密度值列表
    compactValueList_f_gtcv = []
    level_f_gtcv = len(rowInstance_f_gtcv)
    outInstanceIndex_f_gtcv = 0
    while (outInstanceIndex_f_gtcv < level_f_gtcv):
        curInstanceIndex_f_gtcv = rowInstance_f_gtcv[outInstanceIndex_f_gtcv]
        compactValue_f_gtcv = 1.0
        inInstanceIndex_f_gtcv = 0
        while (inInstanceIndex_f_gtcv < level_f_gtcv):
            comparedInstanceIndex_f_gtcv = rowInstance_f_gtcv[inInstanceIndex_f_gtcv]
            if (outInstanceIndex_f_gtcv < inInstanceIndex_f_gtcv):  #当当前实例的id小于被比较实例的id时
                neiIndexMemValueMap_f_gtcv = centerIndex_neiIndex_memValueMap_f_gtcv[curInstanceIndex_f_gtcv]
                compactValue_f_gtcv = min(compactValue_f_gtcv, neiIndexMemValueMap_f_gtcv[comparedInstanceIndex_f_gtcv])
            elif (outInstanceIndex_f_gtcv > inInstanceIndex_f_gtcv):
                compactValue_f_gtcv = min(compactValue_f_gtcv,
                                   centerIndex_neiIndex_memValueMap_f_gtcv[comparedInstanceIndex_f_gtcv][curInstanceIndex_f_gtcv])
            inInstanceIndex_f_gtcv += 1
        compactValueList_f_gtcv.append(compactValue_f_gtcv)
        outInstanceIndex_f_gtcv += 1
    return compactValueList_f_gtcv

def calcTreeFPIforPattern(cliquesInstance_f_ctfp, pattern_f_ctfp,centerIndex_neiIndex_memValueMap_f_ctfp,eventCount_f_ctfp):
    event_instance_compactMap_f_ctfp = {}
    for rowInstance_f_ctfp in cliquesInstance_f_ctfp:  # 获取当前模式所对应的行实例
        compactValueList_f_ctfp = getTreeCompactValue(rowInstance_f_ctfp,centerIndex_neiIndex_memValueMap_f_ctfp)  # 获取当前行实例的紧密度列表

        # 遍历行实例内的每个实例将其紧密度存入每个事件对应的实例字典中event_instance_compactMap_f_gfp即{event:{instance:maxcompactvalue}}
        level_f_ctfp = len(pattern_f_ctfp)
        instanceIndex_f_ctfp = 0
        while (instanceIndex_f_ctfp < level_f_ctfp):  # 遍历行实例
            # 获取当前事件对应的实例紧密度字典，如为空则返回空字典
            instance_compactMap_f_ctfp = event_instance_compactMap_f_ctfp.get(pattern_f_ctfp[instanceIndex_f_ctfp], {})
            # 获取当前实例的紧密度值在字典中存储的紧密度值，如果字典中还没有当前实例的紧密度值则返回0
            compactValue_f_ctfp = instance_compactMap_f_ctfp.get(rowInstance_f_ctfp[instanceIndex_f_ctfp], 0)
            # 比较当前实例与字典中已存储实例的紧密度值，返回最大的以更新该实例的紧密度值
            instance_compactMap_f_ctfp[rowInstance_f_ctfp[instanceIndex_f_ctfp]] = max(compactValue_f_ctfp,
                                                                              compactValueList_f_ctfp[instanceIndex_f_ctfp])            # 更新当前事件对应的实例紧密度字典
            event_instance_compactMap_f_ctfp[pattern_f_ctfp[instanceIndex_f_ctfp]] = instance_compactMap_f_ctfp
            instanceIndex_f_ctfp += 1
    # 如果该模式中不存在表实例则不计算模糊参与度
    fpi_f_ctfp = 1.0

    for event_f_ctfp in pattern_f_ctfp:
        if event_f_ctfp not in event_instance_compactMap_f_ctfp.keys():
            fpi_f_ctfp = 0.0
            break
        eventCompactSum_f_ctfp = sum(event_instance_compactMap_f_ctfp[event_f_ctfp].values())
        curEventCount_f_ctfp = eventCount_f_ctfp[event_f_ctfp]
        fpi_f_ctfp = min(fpi_f_ctfp, eventCompactSum_f_ctfp / curEventCount_f_ctfp)
        fpi_f_ctfp = round(fpi_f_ctfp, 4)
    return fpi_f_ctfp


#----------------------------------------------------------------------------------------------------------
#KDE计算PI的方法
def calcKDETreeFPIforPattern(cliquesInstances_f_ctfp, pattern_f_ctfp,centerIndex_neiIndex_memValueMap_f_ctfp,eventCount_f_ctfp):

    #获取该模式所有的二阶子模式
    subpatternList_f_ckfp = itertools.combinations(pattern_f_ctfp,2)
    #存储各二阶子模式所对应的平均wtb
    meanWtbList_f_ckfp = []
    #针对每个二阶子模式计算pi
    for subpattern_f_ckfp in subpatternList_f_ckfp:
        #得到二阶子模式内两个事件所包含实例的最大值
        maxEventSize_f_ckfp = max([eventCount_f_ctfp[i_list] for i_list in subpattern_f_ckfp])
        #每个事件对应的位置
        posIndex_f_ckfp = [pattern_f_ctfp.index(i_list) for i_list in subpattern_f_ckfp]
        #遍历团实例内该子模式所对应的实例
        subRowInstances_f_ckfp = []
        for cliquesInstance_f_ctfp in cliquesInstances_f_ctfp:
            subRowInstances_f_ckfp.append((cliquesInstance_f_ctfp[posIndex_f_ckfp[0]], cliquesInstance_f_ctfp[posIndex_f_ckfp[1]]))
        #对团实例进行去重过滤
        subRowInstances_f_ckfp = list(set(subRowInstances_f_ckfp))
        #得到所有的距离函数

        wtbList_f_ckfp = []
        for subRowInstance_f_ckfp in subRowInstances_f_ckfp:
         wtbList_f_ckfp.append(centerIndex_neiIndex_memValueMap_f_ctfp[subRowInstance_f_ckfp[0]][subRowInstance_f_ckfp[1]])
        #将所有实例对应的wtb进行求和并计算pi值
        meanWtb_f_ckfp = sum(wtbList_f_ckfp)/(2*maxEventSize_f_ckfp*maxEventSize_f_ckfp)
        meanWtbList_f_ckfp.append(meanWtb_f_ckfp)

    fpi_f_ctfp = min(meanWtbList_f_ckfp)
    return round(fpi_f_ctfp, 4)
