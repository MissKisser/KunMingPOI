<!--
  左侧统计面板
  展示 POI 总量、模式总数等汇总信息，使用 ECharts 饼图呈现类目分布
  @author Hackerdallas
-->
<template>
  <BasicContainer title="总体态势感知">
    <!-- 顶部三个图标卡片 -->
    <div class="top-cards">
      <div class="card-item">
        <IconText1 
          :icon="icon1" 
          label="POI 总量" 
          :value="displayStats[0]?.value || '—'" 
          unit="" 
        />
      </div>
      <div class="card-item v-line-left">
        <IconText1 
          :icon="icon2" 
          label="挖掘模式数" 
          :value="displayStats[1]?.value || '—'" 
          unit="" 
        />
      </div>
      <div class="card-item v-line-left">
        <IconText1 
          :icon="icon3" 
          label="模式实例数" 
          :value="displayStats[2]?.value || '—'" 
          unit="" 
        />
      </div>
    </div>

    <!-- 分隔线 -->
    <div class="divider">
      <div class="h-line"></div>
    </div>

    <!-- 底部两个卡片 -->
    <div class="bottom-cards">
      <div class="card-box">
        <IconText2 
          :icon="icon4" 
          label="类目分布" 
          :value="categoryCount" 
          unit="类" 
        />
      </div>
      <div class="card-box">
        <IconText2 
          :icon="icon5" 
          label="区域覆盖" 
          :value="districtCount" 
          unit="区" 
        />
      </div>
    </div>

    <!-- 图表区域 -->
    <h3 class="panel-subtitle">类目分布态势</h3>
    <div ref="pieEl" class="chart" />

    <h3 class="panel-subtitle">区域模式活跃度</h3>
    <div ref="barEl" class="chart" />
  </BasicContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from './BasicContainer.vue'
import IconText1 from './IconText1.vue'
import IconText2 from './IconText2.vue'
import { useEChartsAutoCarousel } from '../hooks/useEChartsAutoCarousel'

// ─── 图标资源 ─────────────────────────────────────────────────────────────
const icon1 = new URL('@/assets/icon/i-1.svg', import.meta.url).href
const icon2 = new URL('@/assets/icon/i-2.svg', import.meta.url).href
const icon3 = new URL('@/assets/icon/i-3.svg', import.meta.url).href
const icon4 = new URL('@/assets/icon/i-4.svg', import.meta.url).href
const icon5 = new URL('@/assets/icon/i-5.svg', import.meta.url).href

// ─── 汇总数字 ─────────────────────────────────────────────────────────────
interface StatItem { label: string; value: string | number }
const props = defineProps<{ 
  stats?: StatItem[]
  pieData?: { name: string; value: number }[]
  categoryCount?: number
  districtCount?: number
}>()

const displayStats = computed(() => props.stats ?? [
  { label: 'POI 总量', value: '—' },
  { label: '挖掘模式数', value: '—' },
  { label: '模式实例数', value: '—' },
])

const categoryCount = computed(() => props.categoryCount ?? 0)
const districtCount = computed(() => props.districtCount ?? 0)

const pieEl = ref<HTMLDivElement | null>(null)
const barEl = ref<HTMLDivElement | null>(null)

let chart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

const { startRotation: startPieRotation, stopRotation: stopPieRotation } = useEChartsAutoCarousel()
const { startRotation: startBarRotation, stopRotation: stopBarRotation } = useEChartsAutoCarousel()

onMounted(() => {
  chart = echarts.init(pieEl.value!, 'dark')
  barChart = echarts.init(barEl.value!, 'dark')

  const data = props.pieData ?? []
  renderPie(data)

  window.addEventListener('resize', () => {
    chart?.resize()
    barChart?.resize()
  })
})

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
            const colors = ['#3EE5FF', '#2795BB', '#18FEFE', '#96F8FF', '#4fc8ff'];
            return colors[params.dataIndex % colors.length];
          }
        },
        emphasis: { scale: true, scaleSize: 8 },
      },
    ],
  })
  startPieRotation(chart, data.length)
}

function renderDistrictStats(data: { district: string; poi_count: number; pattern_count: number }[]) {
  if (!barChart) return
  barChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.8)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' }
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
  startBarRotation(barChart, data.length)
}

onBeforeUnmount(() => {
  stopPieRotation()
  stopBarRotation()
})

defineExpose({ renderPie, renderDistrictStats })
</script>

<style scoped lang="scss">
.top-cards {
  display: flex;
  padding-top: 8px;
  gap: 0;
}

.card-item {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.v-line-left {
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10%;
    height: 80%;
    width: 1px;
    background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA6 50%, rgba(102, 177, 186, 0) 100%);
  }
}

.divider {
  padding: 12px 8px;
}

.h-line {
  height: 1px;
  background: linear-gradient(90deg, rgba(102, 177, 186, 0) 0%, #539BA6 50%, rgba(102, 177, 186, 0) 100%);
}

.bottom-cards {
  padding: 0 8px 12px;
  display: flex;
  gap: 8px;
}

.card-box {
  flex: 1;
  height: 75px;
}

.panel-subtitle {
  font-size: 15px;
  background: linear-gradient(180deg, #E3FFFE 32%, #ACFFFD 75%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 20px 8px 12px;
  font-family: 'MiSans-Demibold', serif;
  letter-spacing: 0.5px;
}

.chart {
  width: 100%;
  height: 200px;
  padding: 0 8px;
}
</style>
