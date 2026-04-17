<script setup lang="ts">
/**
 * 雷达图组件
 * 用于展示模式的多维度空间特征
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'

interface RadarIndicator {
  name: string
  max: number
}

interface Props {
  data: number[]
  indicators?: RadarIndicator[]
  height?: string
  colors?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  height: '280px',
  indicators: () => [
    { name: '聚集度', max: 1 },
    { name: '紧凑度', max: 1 },
    { name: '空间自相关', max: 1 },
    { name: '密度得分', max: 1 },
    { name: '规模得分', max: 1 },
  ],
  colors: () => ['rgba(62, 229, 255, 0.6)', '#3EE5FF'],
})

const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const { registerChart, unregisterChart } = useEChartsResize()

function initChart() {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value, 'dark')
  registerChart(chart)
  updateChart()
}

function updateChart() {
  if (!chart) return

  chart.setOption({
    radar: {
      indicator: props.indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#fff',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 200, 255, 0.3)',
        },
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 18, 40, 0.3)', 'rgba(0, 18, 40, 0.5)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 200, 255, 0.5)',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: props.data,
            name: '模式特征',
            areaStyle: {
              color: props.colors[0],
            },
            lineStyle: {
              color: props.colors[1],
              width: 2,
            },
            itemStyle: {
              color: props.colors[1],
            },
          },
        ],
        emphasis: {
          areaStyle: {
            color: props.colors[0],
          },
        },
      },
    ],
  })
}

function disposeChart() {
  if (chart) {
    unregisterChart(chart)
    chart.dispose()
    chart = null
  }
}

watch(
  () => props.data,
  () => {
    updateChart()
  },
  { deep: true }
)

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  disposeChart()
})
</script>

<template>
  <div ref="chartEl" class="radar-chart" :style="{ height }"></div>
</template>

<style scoped>
.radar-chart {
  width: 100%;
}
</style>
