<script setup lang="ts">
/**
 * 类别流向桑基图组件
 * 展示 POI 类别在同位模式中的共现流向
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { fetchCategoryFlowSankey, type SankeyData } from '@/api'

interface Props {
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '280px',
})

const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const { registerChart, unregisterChart } = useEChartsResize()

const loading = ref(true)
const error = ref<string | null>(null)

async function loadData() {
  try {
    loading.value = true
    error.value = null
    const data: SankeyData = await fetchCategoryFlowSankey()
    renderSankey(data)
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load sankey data:', e)
  } finally {
    loading.value = false
  }
}

function renderSankey(data: SankeyData) {
  if (!chart) {
    console.warn('[Sankey] Chart not initialized')
    return
  }

  if (!data.nodes || data.nodes.length === 0) {
    console.warn('[Sankey] No nodes data')
    return
  }

  if (!data.links || data.links.length === 0) {
    console.warn('[Sankey] No links data')
    return
  }

  console.log('[Sankey] Rendering with', data.nodes.length, 'nodes and', data.links.length, 'links')

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' },
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<div style="font-weight:bold">${params.name}</div>`
        } else if (params.dataType === 'edge') {
          return `<div>${params.data.source} → ${params.data.target}</div><div>关联强度: ${params.data.value}</div>`
        }
        return ''
      },
    },
    series: [
      {
        type: 'sankey',
        layout: 'none',
        emphasis: {
          focus: 'adjacency',
        },
        nodeAlign: 'justify',
        nodeWidth: 20,
        nodeGap: 12,
        layoutIterations: 32,
        left: '5%',
        right: '5%',
        top: '5%',
        bottom: '5%',
        data: data.nodes.map((node) => ({
          name: node.name,
          depth: node.depth,
          itemStyle: {
            color: getCategoryColor(node.name),
          },
        })),
        links: data.links.map((link) => ({
          source: link.source,
          target: link.target,
          value: link.value,
          lineStyle: {
            color: 'gradient',
            curveness: 0.5,
            opacity: 0.5,
          },
        })),
        lineStyle: {
          color: 'gradient',
          curveness: 0.5,
        },
        label: {
          position: 'right',
          color: '#fff',
          fontSize: 11,
          padding: [0, 0, 0, 4],
          formatter: (params: any) => {
            const name = params.name
            return name.length > 4 ? name.slice(0, 4) : name
          },
        },
        itemStyle: {
          borderWidth: 1,
          borderColor: 'rgba(255, 255, 255, 0.3)',
        },
      },
    ],
  })

  // 确保图表正确渲染
  requestAnimationFrame(() => {
    chart?.resize()
  })
}

function getCategoryColor(name: string): string {
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
  return colorMap[name] || '#3EE5FF'
}

function initChart() {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value, 'dark')
  registerChart(chart)

  // 确保图表容器有正确的尺寸后初始化
  requestAnimationFrame(() => {
    chart?.resize()
  })
}

function disposeChart() {
  if (chart) {
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
  <div class="sankey-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">加载流向数据...</div>
    </div>
    <div v-else-if="error" class="error-overlay">{{ error }}</div>
    <div ref="chartEl" class="sankey-chart" :style="{ height }"></div>
  </div>
</template>

<style scoped>
.sankey-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.sankey-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
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
