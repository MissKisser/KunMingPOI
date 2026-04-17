<!--
  左侧底部卡片 - 区域模式活跃度
  使用 ECharts 横向柱状图展示各区域的模式活跃分布
  @author Hackerdallas
-->
<template>
  <BasicContainer title="区域模式活跃度">
    <div ref="barEl" class="chart" />
  </BasicContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from './BasicContainer.vue'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

const barEl = ref<HTMLDivElement | null>(null)
let barChart: echarts.ECharts | null = null

const { startRotation, stopRotation } = useEChartsAutoCarousel()

function renderDistrictStats(data: { district: string; poi_count: number; pattern_count: number }[]) {
  if (!barChart) return
  barChart.setOption({
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
    grid: { left: 8, right: 30, top: 10, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } },
      axisLabel: { color: '#89a', fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.district),
      axisLabel: { color: '#fff', fontSize: 11, fontFamily: 'MiSans-Normal' },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } }
    },
    series: [
      {
        name: '模式数',
        type: 'bar',
        data: data.map(d => d.pattern_count),
        barMaxWidth: 14,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: 'rgba(62, 229, 255, 0.1)' },
            { offset: 1, color: '#3EE5FF' }
          ]),
          borderRadius: [0, 4, 4, 0],
          shadowBlur: 10,
          shadowColor: 'rgba(62, 229, 255, 0.5)'
        }
      }
    ]
  })
  startRotation(barChart, data.length)
}

onMounted(() => {
  barChart = echarts.init(barEl.value!, 'dark')
  window.addEventListener('resize', () => barChart?.resize())
})

onBeforeUnmount(stopRotation)

defineExpose({ renderDistrictStats })
</script>

<style scoped>
.chart {
  width: 100%;
  height: 240px;
  padding: 8px;
  box-sizing: border-box;
}
</style>
