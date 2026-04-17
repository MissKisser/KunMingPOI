# __*__ coding=utf-8 __*__
#v1.0.0 2018.12.9
import pandas as pd
import BasicToos20250705
import itertools
import copy
import time
import matplotlib.pyplot as plt

#获取星型实例
def genCandidatePatterns(priorPatterns_f_gcp):
    candidatePatterns_f_gcp = []
    #将输入的列表排序
    priorPatterns_f_gcp = sorted(priorPatterns_f_gcp)
    for loop_pattern_f_gcp in priorPatterns_f_gcp:
        curLoopPatternIndex_f_gcp = priorPatterns_f_gcp.index(loop_pattern_f_gcp)  # 获取当前遍历的模式在已排序模式列表中的位置
        for innerLoop_pattern_f_gcp in priorPatterns_f_gcp[curLoopPatternIndex_f_gcp + 1:]:  # 遍历当前模式之后的模式与当前实例的比较
            if (loop_pattern_f_gcp[0:len(loop_pattern_f_gcp) - 1] == innerLoop_pattern_f_gcp[
                                                                     0:len(loop_pattern_f_gcp) - 1]):
                candidatePatterns_f_gcp.append(loop_pattern_f_gcp + innerLoop_pattern_f_gcp[-1])
            else:
                break
    return candidatePatterns_f_gcp

#根据模式产生星型实例
def getStarInstance(candidatePatterns_f_gsi, centerIndexEventNeiIndexMap_f_gsi):
    patternStarInstanceDic_f_gsi = {}
    for centerIndex_f_gsi in centerIndexEventNeiIndexMap_f_gsi:
        #获取本行星型邻居表中的所有事件
        eventList_f_gsi = list(centerIndexEventNeiIndexMap_f_gsi[centerIndex_f_gsi].keys())
        eventList_f_gsi.append(idInstanceMap[centerIndex_f_gsi][1])
        eventList_f_gsi.sort()
        #如果候选模式包含在星型邻居的事件集中，通过事件集产生星型实例
        for candidatePattern_f_gsi in candidatePatterns_f_gsi:
            if(len([i for i in candidatePattern_f_gsi if i in eventList_f_gsi]) == len(candidatePattern_f_gsi)and
            candidatePattern_f_gsi[0] == idInstanceMap[centerIndex_f_gsi][1]):
                tempDic_f_gsi = copy.copy(centerIndexEventNeiIndexMap_f_gsi[centerIndex_f_gsi])
                tempDic_f_gsi[idInstanceMap[centerIndex_f_gsi][1]] = [centerIndex_f_gsi]
                #将每个事件对应的实例放入列表中[[事件A对应的实例],[事件B对应的实例}，[事件C对应的实例]]
                instanceListList_f_gsi = []
                #获取事件对应的实例列表
                for event_f_gsi in candidatePattern_f_gsi:
                    instanceListList_f_gsi.append(tempDic_f_gsi[event_f_gsi])
                #将事件对应的实例列表做笛卡尔乘积，并将结果（星型实例）放入starInstanceList_f_gsi中
                starInstanceList_f_gsi = []
                if(len(instanceListList_f_gsi) == 0):
                    continue
                for starInstance_f_gsi in  itertools.product(*instanceListList_f_gsi):
                    if(starInstance_f_gsi[0] == centerIndex_f_gsi):
                        starInstanceList_f_gsi.append(starInstance_f_gsi)
                tempList_f_gsi = patternStarInstanceDic_f_gsi.get(candidatePattern_f_gsi,[])
                tempList_f_gsi.extend(starInstanceList_f_gsi)
                patternStarInstanceDic_f_gsi[candidatePattern_f_gsi] = tempList_f_gsi
    print("星型实例为patternStarInstanceDic_f_gsi：",patternStarInstanceDic_f_gsi)
    return  patternStarInstanceDic_f_gsi

#获取compcValue列表
# 计算模式的紧密度
def getCompactValue(rowInstance):
    cliqueFlag = True  #判断当前行实例是否为团
    # 返回值为rowInstance内部每个实例在行实例中的紧密度值列表
    compactValueList = []
    level = len(rowInstance)
    outInstanceIndex = 0
    while (outInstanceIndex < level):
        curInstanceIndex = rowInstance[outInstanceIndex]
        compactValue = 1.0
        inInstanceIndex = 0
        while (inInstanceIndex < level):
            comparedInstanceIndex = rowInstance[inInstanceIndex]
            if (outInstanceIndex < inInstanceIndex):
                if(curInstanceIndex not in centerIndex_neiIndex_memValueMap.keys()):
                    cliqueFlag = False
                    break
                neiIndexMemValueMap_f_gcv = centerIndex_neiIndex_memValueMap[curInstanceIndex]
                if(comparedInstanceIndex not in neiIndexMemValueMap_f_gcv.keys()):
                    cliqueFlag = False
                    break
                compactValue = min(compactValue, neiIndexMemValueMap_f_gcv[comparedInstanceIndex])
            elif (outInstanceIndex > inInstanceIndex):
                if (comparedInstanceIndex not in centerIndex_neiIndex_memValueMap.keys()):
                    cliqueFlag = False
                    break
                if (curInstanceIndex not in centerIndex_neiIndex_memValueMap[comparedInstanceIndex].keys()):
                    cliqueFlag = False
                    break
                compactValue = min(compactValue,centerIndex_neiIndex_memValueMap[comparedInstanceIndex][curInstanceIndex])
            inInstanceIndex += 1
        if(cliqueFlag == False):
            break
        compactValueList.append(compactValue)
        outInstanceIndex += 1
    return cliqueFlag, compactValueList

#获取频繁模式
def getFrequentPattern(patternStarInstanceDic_f_gfp):
    print("开始计算FPI")
    pattern_Fpi_f_gfp = {}
    frequentPattern_starInstance_f_gfp = {}
    #__________________________________________________________
    #存储模式
    for pattern_f_gfp in patternStarInstanceDic_f_gfp.keys():
        event_instance_compactMap_f_gfp = {}
        if (len(patternStarInstanceDic_f_gfp[pattern_f_gfp]) == 0):
            continue
        for rowInstance_f_gfp in patternStarInstanceDic_f_gfp[pattern_f_gfp]:
            cliqueFlag, compactValueList = getCompactValue(rowInstance_f_gfp)
            if(cliqueFlag == False):
                continue
            level = len(pattern_f_gfp)
            instanceIndex = 0
            while (instanceIndex < level):
                instance_compactMap = event_instance_compactMap_f_gfp.get(pattern_f_gfp[instanceIndex], {})
                compactValue = instance_compactMap.get(rowInstance_f_gfp[instanceIndex], 0)
                instance_compactMap[rowInstance_f_gfp[instanceIndex]] = max(compactValue,
                                                                            compactValueList[instanceIndex])
                event_instance_compactMap_f_gfp[pattern_f_gfp[instanceIndex]] = instance_compactMap
                instanceIndex += 1
        #如果该模式中不存在表实例则不计算模糊参与度
        fpi = 1.0
        for event in pattern_f_gfp:
            if(event not in event_instance_compactMap_f_gfp.keys()):
                fpi = 0.0
                break
            eventCompactSum = sum(event_instance_compactMap_f_gfp[event].values())
            curEventCount = eventCount[event]
            fpi = min(fpi, eventCompactSum / curEventCount)
            fpi = round(fpi, 4)
        if (fpi >= fpiThreshold):
            frequentPattern_starInstance_f_gfp[pattern_f_gfp] = patternStarInstanceDic_f_gfp[pattern_f_gfp]
            pattern_Fpi_f_gfp[pattern_f_gfp] = fpi
    print("频繁模式为：", len(pattern_Fpi_f_gfp), pattern_Fpi_f_gfp)
    # 为频繁模式设置标签
    return pattern_Fpi_f_gfp, frequentPattern_starInstance_f_gfp

#读取数据
if __name__ == "__main__":
    startTime = time.time()
    fpiThreshold = 0.3
    memValueTheshold = 0.1
    absolutDistance = 20
    distanceThreshold = 150

    #生成邻居列表
    idInstanceMap, instanceIdMap, eventCount, centerIndex_neiIndex_memValueMap, patternDisMap = \
        BasicToos20250705.getStarNei("F:\数据集\smallplant(real1).data",absolutDistance,distanceThreshold,memValueTheshold,disfuncType=2)
    print("经典邻居个数为：", len(centerIndex_neiIndex_memValueMap))
    # 具体距离在经典算法中无用，将centerIndex_neiIndex_memValueMap改为centerIndexEventNeiIndexMap
    centerIndexEventNeiIndexMap = {}
    for centerIndex in centerIndex_neiIndex_memValueMap.keys():
        tempDic = {}
        for neiIndex in centerIndex_neiIndex_memValueMap[centerIndex]:
            tempInstance = idInstanceMap[neiIndex]
            tempList = tempDic.get(tempInstance[1], [])
            tempList.append(neiIndex)
            tempDic[tempInstance[1]] = tempList
        centerIndexEventNeiIndexMap[centerIndex] = tempDic
    # 生成二阶表实例
    candidatePatterns = genCandidatePatterns(list(eventCount.keys()))
    patternStarInstanceDic = getStarInstance(candidatePatterns, centerIndexEventNeiIndexMap)
    print("patternStarInstanceDic:",patternStarInstanceDic)
    patternFpi,freqPatternTableInstance = getFrequentPattern(patternStarInstanceDic)

    sorted_patternFpi = dict(sorted(patternFpi.items(), key=lambda item: item[1], reverse=True))
    print("2阶频繁模式有：", sorted_patternFpi)

    while len(patternFpi) > 0:
        candidatePatterns = genCandidatePatterns(list(patternFpi.keys()))
        print("本次候选模式有",candidatePatterns)
        patternStarInstanceDic = getStarInstance(candidatePatterns,centerIndexEventNeiIndexMap)
        patternFpi, freqPatternTableInstance = getFrequentPattern(patternStarInstanceDic)
        sorted_patternFpi = dict(sorted(patternFpi.items(), key=lambda item: item[1], reverse=True))
        print("频繁模式有：", sorted_patternFpi)

    endTime = time.time()
    print("耗时：",endTime-startTime)

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


