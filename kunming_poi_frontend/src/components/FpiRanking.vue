<!--
  FPI 高频模式排行榜面板
  从后端拉取 /api/fpi-ranking，以 ECharts 横向柱状图展示
  @author Hackerdallas
-->
<template>
  <div class="panel ranking-panel">
    <div ref="chartEl" class="chart ranking-chart" />
    <h3 class="panel-subtitle">核心模式类目占比</h3>
    <div ref="categoryBarEl" class="chart category-bar-chart" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { fetchFpiRanking, fetchPatternWordcloud } from '../api/index'
import type { FpiRankItem } from '../api/index'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

const props = defineProps({
  limit: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits<{
  (e: 'pattern-click', patternId: number): void
}>()

const chartEl = ref<HTMLDivElement | null>(null)
const categoryBarEl = ref<HTMLDivElement | null>(null)

let chart: echarts.ECharts | null = null
let categoryBarChart: echarts.ECharts | null = null

const { startRotation: startRankRotation, stopRotation: stopRankRotation } = useEChartsAutoCarousel()
const { startRotation: startCatRotation, stopRotation: stopCatRotation } = useEChartsAutoCarousel()

const rankData = ref<FpiRankItem[]>([])

async function loadRanking() {
  const [rankingData, wordcloudData] = await Promise.all([
    fetchFpiRanking(props.limit),
    fetchPatternWordcloud()
  ])
  rankData.value = rankingData
  renderChart(rankingData)
  renderCategoryBar(wordcloudData)
}

function renderChart(data: FpiRankItem[]) {
  if (!chart) return

  const names = data.map((d) => d.pattern_name).reverse()
  const supports = data.map((d) => d.fpi_score).reverse()
  const patternIds = data.map((d) => d.pattern_id).reverse()

  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 30, top: 10, bottom: 0, containLabel: true },
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.8)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' }
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

  startRankRotation(chart, data.length)
}

function renderCategoryBar(data: { name: string; value: number }[]) {
  if (!categoryBarChart) return
  categoryBarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' }
    },
    grid: { left: 30, right: 30, top: 20, bottom: 30, containLabel: true },
    xAxis: { 
      type: 'category', 
      data: data.map(d => d.name),
      axisLabel: { 
        color: '#fff', 
        fontSize: 10, 
        fontFamily: 'MiSans-Normal',
        rotate: 45,
        interval: 0
      },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } }, 
      axisLabel: { color: '#89a', fontSize: 10 }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        data: data.map(d => d.value),
        barMaxWidth: 30,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: 'rgba(62, 229, 255, 0.1)' }, 
            { offset: 1, color: '#3EE5FF' }
          ]),
          borderRadius: [4, 4, 0, 0],
          shadowBlur: 10,
          shadowColor: 'rgba(62, 229, 255, 0.5)'
        }
      }
    ]
  })
  startCatRotation(categoryBarChart, data.length)
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  categoryBarChart = echarts.init(categoryBarEl.value!, 'dark')
  loadRanking()

  window.addEventListener('resize', () => {
    chart?.resize()
    categoryBarChart?.resize()
  })
})

onBeforeUnmount(() => {
  stopRankRotation()
  stopCatRotation()
})
</script>

<style scoped>
.ranking-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  width: 100%;
}

.panel-subtitle {
  font-size: 14px;
  background: linear-gradient(180deg, #E3FFFE 32%, #ACFFFD 75%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 16px 0 8px;
  padding: 0 4px;
  font-family: 'MiSans-Demibold', serif;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.ranking-chart {
  width: 100%;
  flex: 1;
  min-height: 200px;
  padding: 8px 0;
}

.category-bar-chart {
  width: 100%;
  flex: 1;
  min-height: 150px;
  padding: 8px 0;
}
</style>
