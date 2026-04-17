<script setup lang="ts">
/**
 * 模式关系网络图组件
 * 展示模式之间的相似性关系网络
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { fetchPatternNetwork, type PatternNetwork } from '@/api'

interface Props {
  minWeight?: number
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  minWeight: 0.3,
  height: '280px',
})

const emit = defineEmits<{
  (e: 'pattern-click', patternId: number): void
}>()

const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let animationTimer: number | null = null
const { registerChart, unregisterChart } = useEChartsResize()

const loading = ref(true)
const error = ref<string | null>(null)

async function loadData() {
  try {
    loading.value = true
    error.value = null
    const data: PatternNetwork = await fetchPatternNetwork(props.minWeight)
    renderNetwork(data)
    startContinuousAnimation()
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load network data:', e)
  } finally {
    loading.value = false
  }
}

function getCategoryColor(category: string): string {
  const colorMap: Record<string, string> = {
    购物消费: '#FF6B6B',
    科教文化: '#4ECDC4',
    医疗保健: '#45B7D1',
    汽车相关: '#FFA07A',
    生活服务: '#98D8C8',
    交通设施: '#F7DC6F',
    餐饮美食: '#BB8FCE',
    休闲娱乐: '#F8B739',
    运动健身: '#52C41A',
  }
  return colorMap[category] || '#3EE5FF'
}

function startContinuousAnimation() {
  if (animationTimer) {
    clearInterval(animationTimer)
  }
  animationTimer = window.setInterval(() => {
    if (chart) {
      const option = chart.getOption() as any
      if (option && option.series && option.series[0]) {
        chart.setOption({
          series: [{
            ...option.series[0],
            force: {
              ...option.series[0].force,
              layoutAnimation: true,
            }
          }]
        }, { lazyUpdate: true })
      }
    }
  }, 3000)
}

function renderNetwork(data: PatternNetwork) {
  if (!chart) return

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `
            <div style="font-weight:bold;margin-bottom:4px">${params.data.name}</div>
            <div>FPI: ${params.data.value?.toFixed(4) || 'N/A'}</div>
            <div>类别: ${params.data.category || 'N/A'}</div>
          `
        } else if (params.dataType === 'edge') {
          return `相似度: ${params.data.weight?.toFixed(3) || 'N/A'}`
        }
        return ''
      },
    },
    legend: {
      show: true,
      orient: 'vertical',
      right: 10,
      top: 10,
      textStyle: {
        color: '#fff',
        fontSize: 10,
      },
      data: [...new Set(data.nodes.map((n) => n.category))],
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        animation: true,
        animationDuration: 1500,
        animationEasingUpdate: 'quinticInOut',
        draggable: true,
        data: data.nodes.map((n) => ({
          id: String(n.id),
          name: n.name,
          value: n.value,
          category: n.category,
          symbolSize: Math.sqrt(n.value) * 15 + 8,
          itemStyle: {
            color: getCategoryColor(n.category),
          },
          label: {
            show: true,
            fontSize: 9,
            color: '#fff',
            formatter: (params: any) => {
              const name = params.data.name
              return name.length > 6 ? name.slice(0, 6) + '...' : name
            },
          },
        })),
        links: data.edges.map((e) => ({
          source: String(e.source),
          target: String(e.target),
          weight: e.weight,
          lineStyle: {
            width: e.weight * 5,
            curveness: 0.2,
            opacity: 0.5,
            color: 'rgba(62, 229, 255, 0.4)',
          },
        })),
        categories: [...new Set(data.nodes.map((n) => n.category))].map((cat) => ({
          name: cat,
          itemStyle: {
            color: getCategoryColor(cat),
          },
        })),
        force: {
          repulsion: 150,
          edgeLength: [30, 150],
          gravity: 0.15,
          layoutAnimation: true,
          friction: 0.6,
        },
        roam: true,
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4,
          },
        },
        blur: {
          itemStyle: {
            opacity: 0.3,
          },
          lineStyle: {
            opacity: 0.1,
          },
        },
      },
    ],
  })
}

function initChart() {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value, 'dark')
  registerChart(chart)

  chart.on('click', (params: any) => {
    if (params.dataType === 'node' && params.data?.id) {
      emit('pattern-click', parseInt(params.data.id))
    }
  })
}

function disposeChart() {
  if (animationTimer) {
    clearInterval(animationTimer)
    animationTimer = null
  }
  if (chart) {
    chart.off('click')
    unregisterChart(chart)
    chart.dispose()
    chart = null
  }
}

onMounted(() => {
  initChart()
  loadData()
})

onUnmounted(() => {
  disposeChart()
})

defineExpose({
  refresh: loadData,
})
</script>

<template>
  <div class="network-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">加载网络数据...</div>
    </div>
    <div v-else-if="error" class="error-overlay">{{ error }}</div>
    <div ref="chartEl" class="network-chart" :style="{ height }"></div>
  </div>
</template>

<style scoped>
.network-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.network-chart {
  width: 100%;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 18, 40, 0.8);
  z-index: 10;
}

.loading-text {
  color: #3EE5FF;
  font-size: 14px;
}

.error-overlay {
  color: #ff6b6b;
  font-size: 14px;
}
</style>
