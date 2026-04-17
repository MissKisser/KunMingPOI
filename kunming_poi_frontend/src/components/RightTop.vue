<!--
  右侧顶部卡片 - FPI 高频模式排行
  从后端拉取 /api/fpi-ranking，以 ECharts 横向柱状图展示排行前 10
  点击柱条触发 pattern-click 事件，联动地图散点渲染
  @author Hackerdallas
-->
<template>
  <BasicContainer title="空间高频模式 (FPI) 排行">
    <div ref="chartEl" class="chart" />
  </BasicContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from './BasicContainer.vue'
import { fetchFpiRanking } from '../api/index'
import type { FpiRankItem } from '../api/index'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

const emit = defineEmits<{
  (e: 'pattern-click', patternId: number): void
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const { startRotation, stopRotation } = useEChartsAutoCarousel()

async function loadRanking() {
  const data = await fetchFpiRanking(10)
  renderChart(data)
}

function renderChart(data: FpiRankItem[]) {
  if (!chart) return

  const names = data.map(d => d.pattern_name).reverse()
  const supports = data.map(d => d.fpi_score).reverse()
  const patternIds = data.map(d => d.pattern_id).reverse()

  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 30, top: 10, bottom: 0, containLabel: true },
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
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } },
      axisLabel: { color: '#89a', fontSize: 10 },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#fff', fontSize: 11, fontFamily: 'MiSans-Normal' },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } },
    },
    series: [
      {
        type: 'bar',
        data: supports,
        barMaxWidth: 16,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: 'rgba(79, 200, 255, 0.1)' },
            { offset: 1, color: '#4fc8ff' },
          ]),
          borderRadius: [0, 4, 4, 0],
          shadowBlur: 10,
          shadowColor: 'rgba(79, 200, 255, 0.4)'
        },
        emphasis: {
          itemStyle: { color: '#00e5ff', shadowBlur: 20 },
        },
      },
    ],
  })

  chart.off('click')
  chart.on('click', (params: any) => {
    const idx = data.length - 1 - Number(params.dataIndex)
    if (idx >= 0 && idx < patternIds.length) {
      const pid = patternIds[idx]
      if (pid !== undefined) {
        emit('pattern-click', pid)
      }
    }
  })

  startRotation(chart, data.length)
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  loadRanking()
  window.addEventListener('resize', () => chart?.resize())
})

onBeforeUnmount(stopRotation)
</script>

<style scoped>
.chart {
  width: 100%;
  height: 320px;
  padding: 8px 0;
  box-sizing: border-box;
}
</style>
