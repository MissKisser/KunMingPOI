<script setup lang="ts">
/**
 * 区域×类别×模式数 3D 柱状图组件
 * 三维展示各区域各类别的模式数量
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { fetchDistrictCategoryPattern3D, type DistrictCategoryPattern3D } from '@/api'

interface Props {
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '320px',
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
    const data: DistrictCategoryPattern3D = await fetchDistrictCategoryPattern3D()
    render3DBar(data)
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load 3D data:', e)
  } finally {
    loading.value = false
  }
}

function render3DBar(data: DistrictCategoryPattern3D) {
  if (!chart) return

  const maxValue = Math.max(...data.values.flat())

  chart.setOption({
    visualMap: {
      show: true,
      min: 0,
      max: maxValue,
      inRange: {
        color: [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026',
        ],
      },
      textStyle: {
        color: '#fff',
      },
      right: 10,
      top: 'center',
    },
    xAxis3D: {
      type: 'category',
      data: data.districts,
      name: '区域',
      nameTextStyle: {
        color: '#fff',
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
        rotate: 45,
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(62, 229, 255, 0.5)',
        },
      },
    },
    yAxis3D: {
      type: 'category',
      data: data.categories,
      name: '类别',
      nameTextStyle: {
        color: '#fff',
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(62, 229, 255, 0.5)',
        },
      },
    },
    zAxis3D: {
      type: 'value',
      name: '模式数',
      nameTextStyle: {
        color: '#fff',
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(62, 229, 255, 0.5)',
        },
      },
    },
    grid3D: {
      boxWidth: 180,
      boxDepth: 80,
      boxHeight: 80,
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 8,
        distance: 220,
        alpha: 25,
        beta: 40,
      },
      light: {
        main: {
          intensity: 1.2,
          shadow: true,
        },
        ambient: {
          intensity: 0.3,
        },
      },
      environment: 'none',
    },
    series: [
      {
        type: 'bar3D',
        data: data.districts.flatMap((_, i) =>
          data.categories.map((_, j) => ({
            value: [i, j, data.values[i]?.[j] ?? 0],
          }))
        ),
        shading: 'lambert',
        label: {
          fontSize: 10,
          borderWidth: 1,
          show: false,
        },
        itemStyle: {
          opacity: 0.9,
        },
        emphasis: {
          itemStyle: {
            color: '#FFD700',
          },
          label: {
            fontSize: 14,
            show: true,
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
  <div class="bar3d-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">加载 3D 数据...</div>
    </div>
    <div v-else-if="error" class="error-overlay">{{ error }}</div>
    <div ref="chartEl" class="bar3d-chart" :style="{ height }"></div>
  </div>
</template>

<style scoped>
.bar3d-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.bar3d-chart {
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
