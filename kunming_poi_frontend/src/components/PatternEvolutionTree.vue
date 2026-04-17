<script setup lang="ts">
/**
 * 模式演化树组件
 * 可视化 2阶→3阶→4阶 模式的演化关系
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { fetchPatternEvolution, fetchFpiRanking, type PatternEvolution, type FpiRankItem } from '@/api'

interface Props {
  patternId?: number
  maxLevel?: number
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  patternId: undefined,
  maxLevel: 4,
  height: '260px',
})

const emit = defineEmits<{
  (e: 'pattern-click', patternId: number): void
}>()

const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const { registerChart, unregisterChart } = useEChartsResize()

const loading = ref(true)
const error = ref<string | null>(null)
const evolutionData = ref<Map<number, PatternEvolution>>(new Map())
const allPatterns = ref<FpiRankItem[]>([])

const levelColors: Record<number, string> = {
  2: '#3EE5FF',
  3: '#4ECDC4',
  4: '#FF6B6B',
}

async function loadData() {
  try {
    loading.value = true
    error.value = null

    // 获取 FPI 排行榜作为根节点
    allPatterns.value = await fetchFpiRanking(30)

    if (allPatterns.value.length === 0) {
      error.value = '暂无模式数据'
      return
    }

    // 获取前几个模式的演化数据
    const patternsToLoad = props.patternId
      ? allPatterns.value.filter(p => p.pattern_id === props.patternId).concat(allPatterns.value.slice(0, 10))
      : allPatterns.value.slice(0, 15)

    const evolutionPromises = patternsToLoad.map(async (p) => {
      try {
        const evolution = await fetchPatternEvolution(p.pattern_id)
        evolutionData.value.set(p.pattern_id, evolution)
        return evolution
      } catch {
        return null
      }
    })

    await Promise.all(evolutionPromises)
    renderTree()
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load evolution data:', e)
  } finally {
    loading.value = false
  }
}

function buildTreeData(): any {
  const visited = new Set<number>()

  function buildNode(pattern: FpiRankItem, level: number): any {
    if (visited.has(pattern.pattern_id)) {
      return null
    }
    visited.add(pattern.pattern_id)

    const evolution = evolutionData.value.get(pattern.pattern_id)
    const children: any[] = []

    if (evolution && evolution.child_patterns && evolution.child_patterns.length > 0 && level < props.maxLevel) {
      evolution.child_patterns.forEach((childId) => {
        const childPattern = allPatterns.value.find((p) => p.pattern_id === childId)
        if (childPattern && !visited.has(childId)) {
          const childNode = buildNode(childPattern, level + 1)
          if (childNode) {
            children.push(childNode)
          }
        }
      })
    }

    return {
      name: pattern.pattern_name,
      pattern_id: pattern.pattern_id,
      fpi: pattern.fpi_score,
      level,
      value: pattern.fpi_score,
      itemStyle: {
        color: levelColors[level] || '#3EE5FF',
      },
      children: children.length > 0 ? children : undefined,
    }
  }

  // 如果有选中的模式，以它为中心构建
  if (props.patternId) {
    const selectedPattern = allPatterns.value.find(p => p.pattern_id === props.patternId)
    if (selectedPattern) {
      const node = buildNode(selectedPattern, 2)
      if (node) {
        return {
          name: '模式演化',
          children: [node]
        }
      }
    }
  }

  // 从 2 阶模式开始构建树
  const rootPatterns = allPatterns.value.filter((p) => {
    const len = p.pattern_name.split('-').length
    return len === 2
  }).slice(0, 8)

  if (rootPatterns.length === 0) {
    // 如果没有2阶模式，取前8个模式
    return {
      name: '模式演化',
      children: allPatterns.value.slice(0, 8).map((p) => buildNode(p, 2)).filter(Boolean),
    }
  }

  return {
    name: '模式演化',
    children: rootPatterns.map((p) => buildNode(p, 2)).filter(Boolean),
  }
}

function renderTree() {
  if (!chart) return

  const treeData = buildTreeData()

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        if (params.data?.pattern_id) {
          return `
            <div style="font-weight:bold;margin-bottom:4px">${params.data.name}</div>
            <div>阶数: ${params.data.level}</div>
            <div>FPI: ${params.data.fpi?.toFixed(4) || 'N/A'}</div>
          `
        }
        return params.data?.name || ''
      },
    },
    series: [
      {
        type: 'tree',
        data: [treeData],
        top: '8%',
        left: '8%',
        bottom: '8%',
        right: '25%',
        symbolSize: 14,
        symbol: 'circle',
        orient: 'LR',
        initialTreeDepth: 3,
        roam: true,
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left',
          fontSize: 11,
          color: '#fff',
          formatter: (params: any) => {
            const name = params.data?.name || ''
            return name.length > 10 ? name.slice(0, 10) + '...' : name
          },
        },
        leaves: {
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left',
          },
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        lineStyle: {
          color: 'rgba(62, 229, 255, 0.5)',
          width: 1.5,
          curveness: 0.5,
        },
        itemStyle: {
          borderWidth: 2,
          borderColor: '#fff',
        },
        emphasis: {
          focus: 'descendant',
          itemStyle: {
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: 'rgba(62, 229, 255, 0.5)',
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
    if (params.data?.pattern_id) {
      emit('pattern-click', params.data.pattern_id)
    }
  })
}

function disposeChart() {
  if (chart) {
    chart.off('click')
    unregisterChart(chart)
    chart.dispose()
    chart = null
  }
}

watch(
  () => props.maxLevel,
  () => {
    renderTree()
  }
)

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
  <div class="evolution-tree-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">加载演化数据...</div>
    </div>
    <div v-else-if="error" class="error-overlay">{{ error }}</div>
    <div ref="chartEl" class="evolution-tree-chart" :style="{ height }"></div>
  </div>
</template>

<style scoped>
.evolution-tree-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.evolution-tree-chart {
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
