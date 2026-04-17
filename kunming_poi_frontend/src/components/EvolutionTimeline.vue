<script setup lang="ts">
/**
 * 模式演化时间轴组件
 * 动画展示模式 FPI 随时间的演化
 * @author Hackerdallas
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { useEChartsResize } from '@/composables/useEChartsResize'
import { fetchEvolutionTimeline, type EvolutionTimeline } from '@/api'

interface Props {
  steps?: number
  interval?: 'month' | 'quarter'
  height?: string
  autoPlay?: boolean
  loop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  steps: 12,
  interval: 'month',
  height: '240px',
  autoPlay: true,
  loop: true,
})

const emit = defineEmits<{
  (e: 'time-change', step: number, timestamp: string): void
}>()

const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const { registerChart, unregisterChart } = useEChartsResize()

const loading = ref(true)
const error = ref<string | null>(null)
const timelineData = ref<EvolutionTimeline | null>(null)

const currentStep = ref(0)
const isPlaying = ref(false)
let animationTimer: ReturnType<typeof setTimeout> | null = null

const currentTimestamp = computed(() => {
  if (!timelineData.value) return ''
  return timelineData.value.timestamps[currentStep.value] ?? ''
})

async function loadData() {
  try {
    loading.value = true
    error.value = null
    timelineData.value = await fetchEvolutionTimeline(props.steps, props.interval)
    renderTimeline()
    if (props.autoPlay) {
      play()
    }
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load timeline data:', e)
  } finally {
    loading.value = false
  }
}

function renderTimeline() {
  if (!chart || !timelineData.value) return

  const data = timelineData.value
  const step = currentStep.value

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff' },
    },
    legend: {
      show: true,
      top: 5,
      textStyle: {
        color: '#fff',
        fontSize: 10,
      },
      data: data.series.slice(0, 5).map((s) => s.pattern_name),
    },
    grid: {
      left: 40,
      right: 20,
      top: 35,
      bottom: 30,
    },
    xAxis: {
      type: 'category',
      data: data.timestamps.slice(0, step + 1),
      axisLine: {
        lineStyle: { color: 'rgba(0, 200, 255, 0.5)' },
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: 'FPI',
      nameTextStyle: { color: '#fff', fontSize: 10 },
      axisLine: {
        lineStyle: { color: 'rgba(0, 200, 255, 0.5)' },
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 200, 255, 0.15)' },
      },
    },
    series: data.series.slice(0, 5).map((s, index) => ({
      name: s.pattern_name,
      type: 'line',
      data: s.fpi_values.slice(0, step + 1),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2,
      },
      itemStyle: {
        color: getLineColor(index),
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: getLineColor(index, 0.3) },
          { offset: 1, color: getLineColor(index, 0.05) },
        ]),
      },
    })),
  })
}

function getLineColor(index: number, alpha = 1): string {
  const colors: string[] = [
    `rgba(62, 229, 255, ${alpha})`,
    `rgba(78, 205, 196, ${alpha})`,
    `rgba(255, 107, 107, ${alpha})`,
    `rgba(255, 215, 0, ${alpha})`,
    `rgba(187, 143, 206, ${alpha})`,
  ]
  return colors[index % colors.length] ?? colors[0]!
}

function play() {
  if (!timelineData.value) return

  isPlaying.value = true

  const playStep = () => {
    if (!timelineData.value) return

    if (currentStep.value >= timelineData.value.timestamps.length - 1) {
      if (props.loop) {
        currentStep.value = 0
      } else {
        stop()
        return
      }
    } else {
      currentStep.value++
    }

    renderTimeline()
    emit('time-change', currentStep.value, currentTimestamp.value)

    animationTimer = setTimeout(playStep, 2000)
  }

  playStep()
}

function stop() {
  isPlaying.value = false
  if (animationTimer) {
    clearTimeout(animationTimer)
    animationTimer = null
  }
}

function togglePlay() {
  if (isPlaying.value) {
    stop()
  } else {
    play()
  }
}

function reset() {
  stop()
  currentStep.value = 0
  renderTimeline()
}

function goToStep(step: number) {
  if (!timelineData.value) return
  currentStep.value = Math.max(0, Math.min(step, timelineData.value.timestamps.length - 1))
  renderTimeline()
  emit('time-change', currentStep.value, currentTimestamp.value)
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
  stop()
  disposeChart()
})

defineExpose({
  play,
  stop,
  togglePlay,
  reset,
  goToStep,
  refresh: loadData,
})
</script>

<template>
  <div class="timeline-container">
    <!-- 控制栏 -->
    <div class="controls">
      <button class="control-btn toggle" :class="{ playing: isPlaying }" @click="togglePlay">
        <span class="icon">{{ isPlaying ? '⏸' : '▶' }}</span>
        {{ isPlaying ? '暂停' : '播放' }}
      </button>
      <button class="control-btn reset" @click="reset">
        <span class="icon">↺</span>
        重置
      </button>
      <span class="current-time">{{ currentTimestamp }}</span>
      <span v-if="isPlaying" class="loop-hint">循环播放中</span>
    </div>

    <!-- 进度条 -->
    <div v-if="timelineData" class="progress-bar">
      <input
        type="range"
        :value="currentStep"
        :max="timelineData.timestamps.length - 1"
        min="0"
        step="1"
        class="progress-slider"
        @input="goToStep(parseInt(($event.target as HTMLInputElement).value))"
      />
    </div>

    <!-- 图表区域 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">加载时间序列...</div>
    </div>
    <div v-else-if="error" class="error-overlay">{{ error }}</div>
    <div ref="chartEl" class="timeline-chart" :style="{ height }"></div>
  </div>
</template>

<style scoped>
.timeline-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.controls {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(0, 18, 40, 0.6);
  border-bottom: 1px solid rgba(0, 200, 255, 0.2);
  flex-shrink: 0;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 12px;
  background: rgba(62, 229, 255, 0.1);
  border: 1px solid rgba(62, 229, 255, 0.5);
  border-radius: 4px;
  color: #3EE5FF;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  background: rgba(62, 229, 255, 0.2);
}

.control-btn.toggle.playing {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.5);
  color: #FFD700;
}

.control-btn.reset {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
}

.icon {
  font-size: 10px;
}

.current-time {
  margin-left: auto;
  font-size: 12px;
  color: #FFD700;
  font-family: monospace;
}

.loop-hint {
  font-size: 10px;
  color: rgba(62, 229, 255, 0.6);
  margin-left: 8px;
}

.progress-bar {
  padding: 4px 12px;
  background: rgba(0, 18, 40, 0.4);
}

.progress-slider {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(0, 200, 255, 0.3);
  border-radius: 2px;
  outline: none;
}

.progress-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: #3EE5FF;
  border-radius: 50%;
  cursor: pointer;
}

.timeline-chart {
  flex: 1;
  width: 100%;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 60px;
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
