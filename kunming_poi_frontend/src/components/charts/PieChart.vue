<!--
  通用饼图组件
  支持自动轮播、自定义颜色
  @author Hackerdallas
-->
<template>
  <div ref="chartEl" class="chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { useEChartsAutoCarousel } from '@/hooks/useEChartsAutoCarousel'
import { ECHARTS_THEME } from '@/constants'

interface PieDataItem {
  name: string
  value: number
}

const props = withDefaults(defineProps<{
  /** 图表数据 */
  data: PieDataItem[]
  /** 内半径百分比 */
  innerRadius?: string
  /** 外半径百分比 */
  outerRadius?: string
  /** 图表高度 */
  height?: string
  /** 自定义颜色列表 */
  colors?: string[]
}>(), {
  innerRadius: '45%',
  outerRadius: '70%',
  height: '100%',
  colors: () => ['#3EE5FF', '#2795BB', '#18FEFE', '#96F8FF', '#4fc8ff'],
})

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const { registerChart, unregisterChart } = useEChartsResize()
const { startRotation, stopRotation } = useEChartsAutoCarousel()

function renderChart() {
  if (!chart || !props.data.length) return

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: ECHARTS_THEME.TOOLTIP_BG,
      borderColor: ECHARTS_THEME.TOOLTIP_BORDER,
      textStyle: { color: '#fff' }
    },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: [props.innerRadius, props.outerRadius],
      center: ['50%', '50%'],
      data: props.data,
      label: {
        color: ECHARTS_THEME.Y_AXIS_LABEL_COLOR,
        fontSize: ECHARTS_THEME.Y_AXIS_LABEL_FONT_SIZE,
        fontFamily: 'MiSans-Normal'
      },
      itemStyle: {
        borderRadius: 4,
        borderColor: '#060d18',
        borderWidth: 2,
        color: (params: any) => props.colors[params.dataIndex % props.colors.length]
      },
      emphasis: { scale: true, scaleSize: 8 },
    }],
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
