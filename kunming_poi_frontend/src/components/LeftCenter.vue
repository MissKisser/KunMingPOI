<!--
  左侧中部卡片 - 类目分布态势
  使用 ECharts 环形饼图展示各 POI 类目的占比分布
  @author Hackerdallas
-->
<template>
  <BasicContainer title="类目分布态势">
    <div ref="pieEl" class="chart" />
  </BasicContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from './BasicContainer.vue'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

const props = defineProps<{
  pieData?: { name: string; value: number }[]
}>()

const pieEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const { startRotation, stopRotation } = useEChartsAutoCarousel()

function renderPie(data: { name: string; value: number }[]) {
  if (!chart) return
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 20, 38, 0.8)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' }
    },
    legend: { show: false },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        data,
        label: { color: '#fff', fontSize: 11, fontFamily: 'MiSans-Normal' },
        itemStyle: {
          borderRadius: 4,
          borderColor: '#060d18',
          borderWidth: 2,
          color: function(params: any) {
            const colors = ['#3EE5FF', '#2795BB', '#18FEFE', '#96F8FF', '#4fc8ff']
            return colors[params.dataIndex % colors.length]
          }
        },
        emphasis: { scale: true, scaleSize: 8 },
      },
    ],
  })
  startRotation(chart, data.length)
}

onMounted(() => {
  chart = echarts.init(pieEl.value!, 'dark')
  renderPie(props.pieData ?? [])
  window.addEventListener('resize', () => chart?.resize())
})

watch(() => props.pieData, (val) => {
  if (val) renderPie(val)
})

onBeforeUnmount(stopRotation)

defineExpose({ renderPie })
</script>

<style scoped>
.chart {
  width: 100%;
  height: 280px;
  padding: 8px;
  box-sizing: border-box;
}
</style>
