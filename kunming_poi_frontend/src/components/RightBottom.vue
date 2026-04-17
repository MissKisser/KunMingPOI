<!--
  右侧底部卡片 - 核心模式类目占比
  从后端拉取词云数据，以 ECharts 横向柱状图展示各类目模式出现频次
  @author Hackerdallas
-->
<template>
  <BasicContainer title="核心模式类目占比">
    <div ref="categoryBarEl" class="chart" />
  </BasicContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from './BasicContainer.vue'
import { fetchPatternWordcloud } from '../api/index'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

const categoryBarEl = ref<HTMLDivElement | null>(null)
let categoryBarChart: echarts.ECharts | null = null

const { startRotation, stopRotation } = useEChartsAutoCarousel()

async function loadData() {
  const data = await fetchPatternWordcloud()
  renderCategoryBar(data)
}

function renderCategoryBar(data: { name: string; value: number }[]) {
  if (!categoryBarChart) return

  // 按值从小到大排序
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  const names = sortedData.map(d => d.name)
  const values = sortedData.map(d => d.value)

  categoryBarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff', fontSize: 12 },
      confine: true,
      position: (point: number[], _params: any, _dom: any, _rect: any, size: any) => {
        const x = point[0] ?? 0
        const y = point[1] ?? 0
        const contentSize = size?.contentSize ?? [0, 0]
        return { left: x - 10, top: y - contentSize[1] - 10 }
      }
    },
    // 引入垂直滚动支持
    dataZoom: [
      {
        type: 'inside',
        orient: 'vertical',
        startValue: Math.max(0, sortedData.length - 20),
        endValue: sortedData.length - 1
      },
      {
        type: 'slider',
        show: sortedData.length > 10,
        orient: 'vertical',
        right: '2%',
        width: 12,
        borderColor: 'transparent',
        fillerColor: 'rgba(62, 229, 255, 0.2)',
        backgroundColor: 'rgba(0, 0, 0, 0.1)',
        handleStyle: { color: '#3EE5FF' },
        textStyle: { show: false }
      }
    ],
    grid: { left: 10, right: 40, top: 10, bottom: 0, containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } },
      axisLabel: { color: '#89a', fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        color: '#fff',
        fontSize: 11,
        fontFamily: 'MiSans-Normal',
        width: 100,
        overflow: 'truncate'
      },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        data: values,
        barMaxWidth: 16,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: 'rgba(62, 229, 255, 0.1)' },
            { offset: 1, color: '#3EE5FF' }
          ]),
          borderRadius: [0, 4, 4, 0],
          shadowBlur: 10,
          shadowColor: 'rgba(62, 229, 255, 0.4)'
        }
      }
    ]
  })
  startRotation(categoryBarChart, sortedData.length)
}

onMounted(() => {
  categoryBarChart = echarts.init(categoryBarEl.value!, 'dark')
  loadData()
  window.addEventListener('resize', () => categoryBarChart?.resize())
})

onBeforeUnmount(stopRotation)
</script>

<style scoped>
.chart {
  width: 100%;
  height: 380px;
  padding: 8px 0;
  box-sizing: border-box;
}
</style>
