<!--
  通用横向柱状图组件
  支持自动轮播、点击事件、数据缩放
  @author Hackerdallas
-->
<template>
  <div ref="chartEl" class="chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { useEChartsAutoCarousel } from '@/hooks/useEChartsAutoCarousel'
import { ECHARTS_THEME } from '@/constants'

interface BarDataItem {
  name: string
  value: number
  id?: number | string
}

const props = withDefaults(defineProps<{
  /** 图表数据 */
  data: BarDataItem[]
  /** 是否显示数据缩放 */
  showDataZoom?: boolean
  /** 数据缩放阈值（超过此数量显示缩放条） */
  dataZoomThreshold?: number
  /** 渐变色 [起始色, 结束色] */
  gradientColor?: [string, string]
  /** 柱条最大宽度 */
  barMaxWidth?: number
  /** 图表高度 */
  height?: string
}>(), {
  showDataZoom: false,
  dataZoomThreshold: 10,
  gradientColor: () => [ECHARTS_THEME.BAR_GRADIENT_START, ECHARTS_THEME.BAR_GRADIENT_END],
  barMaxWidth: ECHARTS_THEME.BAR_MAX_WIDTH,
  height: '100%',
})

const emit = defineEmits<{
  (e: 'bar-click', item: BarDataItem): void
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const { registerChart, unregisterChart } = useEChartsResize()
const { startRotation, stopRotation } = useEChartsAutoCarousel()

// 数据排序（从小到大）
const sortedData = computed(() =>
  [...props.data].sort((a, b) => a.value - b.value)
)

function renderChart() {
  if (!chart || !props.data.length) return

  const names = sortedData.value.map(d => d.name)
  const values = sortedData.value.map(d => d.value)

  const shouldShowDataZoom = props.showDataZoom && props.data.length > props.dataZoomThreshold

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: ECHARTS_THEME.TOOLTIP_BG,
      borderColor: ECHARTS_THEME.TOOLTIP_BORDER,
      textStyle: { color: '#fff' }
    },
    dataZoom: shouldShowDataZoom ? [
      {
        type: 'inside',
        orient: 'vertical',
        startValue: Math.max(0, props.data.length - 20),
        endValue: props.data.length - 1
      },
      {
        type: 'slider',
        orient: 'vertical',
        right: '2%',
        width: 12,
        borderColor: 'transparent',
        fillerColor: 'rgba(62, 229, 255, 0.2)',
        backgroundColor: 'rgba(0, 0, 0, 0.1)',
        handleStyle: { color: ECHARTS_THEME.TOOLTIP_BORDER },
        textStyle: { show: false }
      }
    ] : undefined,
    grid: ECHARTS_THEME.GRID_BASE,
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: ECHARTS_THEME.SPLIT_LINE, type: 'dashed' } },
      axisLabel: { color: ECHARTS_THEME.AXIS_LABEL_COLOR, fontSize: ECHARTS_THEME.AXIS_LABEL_FONT_SIZE },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        color: ECHARTS_THEME.Y_AXIS_LABEL_COLOR,
        fontSize: ECHARTS_THEME.Y_AXIS_LABEL_FONT_SIZE,
        fontFamily: 'MiSans-Normal',
        width: 100,
        overflow: 'truncate'
      },
      axisLine: { lineStyle: { color: ECHARTS_THEME.Y_AXIS_LINE_COLOR } },
    },
    series: [{
      type: 'bar',
      data: values,
      barMaxWidth: props.barMaxWidth,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: props.gradientColor[0] },
          { offset: 1, color: props.gradientColor[1] },
        ]),
        borderRadius: ECHARTS_THEME.BAR_BORDER_RADIUS,
        shadowBlur: ECHARTS_THEME.BAR_SHADOW_BLUR,
        shadowColor: ECHARTS_THEME.BAR_SHADOW_COLOR
      },
      emphasis: {
        itemStyle: {
          color: ECHARTS_THEME.EMPHASIS_COLOR,
          shadowBlur: ECHARTS_THEME.EMPHASIS_SHADOW_BLUR
        }
      }
    }]
  })

  // 点击事件
  chart.off('click')
  chart.on('click', (params: any) => {
    const idx = sortedData.value.length - 1 - params.dataIndex
    const item = sortedData.value[idx]
    if (item) {
      emit('bar-click', item)
    }
  })

  startRotation(chart, props.data.length)
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  registerChart(chart)
  renderChart()
})

watch(() => props.data, renderChart, { deep: true })

onBeforeUnmount(() => {
  stopRotation()
  unregisterChart(chart)
  chart?.dispose()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: v-bind(height);
}
</style>
