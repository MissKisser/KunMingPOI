<!--
  区域分析独立页面
  深度分析各行政区划的 POI 分布和模式特征
  @author Hackerdallas
-->
<template>
  <div class="districts-view">
    <!-- 顶部：区域选择器 -->
    <header class="district-header">
      <div class="header-left">
        <h1 class="page-title">区域分析</h1>
        <p class="page-desc">昆明市各行政区划 POI 空间分布与模式特征分析</p>
      </div>
      <div class="district-selector">
        <label>选择区域：</label>
        <select v-model="selectedDistrict" class="selector">
          <option value="">全部区域</option>
          <option v-for="d in districts" :key="d.name" :value="d.name">
            {{ d.name }}
          </option>
        </select>
        <button class="carousel-btn" :class="{ active: isAutoPlaying }" @click="toggleAutoPlay" :title="isAutoPlaying ? '暂停轮播' : '自动轮播'">
          <span v-if="isAutoPlaying">⏸</span>
          <span v-else>▶</span>
        </button>
      </div>
    </header>

    <!-- 轮播进度条 -->
    <div class="carousel-progress" v-if="isAutoPlaying">
      <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
      <div class="progress-labels">
        <span v-for="(d, idx) in districts" :key="d.name"
              :class="['progress-dot', { active: currentDistrictIndex === idx }]"
              @click="jumpToDistrict(idx)">
        </span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-area">
      <!-- 左侧：区域统计 -->
      <aside class="stats-panel">
        <BasicContainer title="区域概览" width="100%" :height="200">
          <div class="overview-stats">
            <div class="stat-card">
              <span class="stat-value">{{ totalPoiCount.toLocaleString() }}</span>
              <span class="stat-label">POI 总数</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ totalPatternCount }}</span>
              <span class="stat-label">模式数量</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ districts.length }}</span>
              <span class="stat-label">行政区划</span>
            </div>
          </div>
        </BasicContainer>

        <BasicContainer title="区域排行" width="100%" height="calc(100% - 220px)">
          <div ref="rankingChart" class="chart" />
        </BasicContainer>
      </aside>

      <!-- 中间：地图与3D可视化 -->
      <main class="map-area">
        <div class="map-container">
          <MapView ref="mapView" class="district-map" />
        </div>

        <!-- 3D 柱状图 -->
        <div class="chart-3d">
          <BasicContainer title="区域-类别分布" width="100%" height="100%">
            <DistrictCategory3D :district="selectedDistrict" />
          </BasicContainer>
        </div>
      </main>

      <!-- 右侧：类别分布 -->
      <aside class="category-panel">
        <BasicContainer title="类别分布" width="100%" :height="280">
          <div ref="categoryPieChart" class="chart" />
        </BasicContainer>

        <BasicContainer title="区域详情" width="100%" height="calc(100% - 300px)">
          <div class="district-detail" v-if="currentDistrictData">
            <div class="detail-item">
              <span class="detail-label">区域名称</span>
              <span class="detail-value">{{ currentDistrictData.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">POI 数量</span>
              <span class="detail-value">{{ currentDistrictData.poi_count?.toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">模式数量</span>
              <span class="detail-value">{{ currentDistrictData.pattern_count }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">POI 占比</span>
              <span class="detail-value">{{ poiPercentage }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">模式占比</span>
              <span class="detail-value">{{ patternPercentage }}%</span>
            </div>
          </div>
          <div class="no-selection" v-else>
            <p>点击地图或选择区域查看详情</p>
          </div>
        </BasicContainer>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from '../components/BasicContainer.vue'
import MapView from '../components/MapView.vue'
import DistrictCategory3D from '../components/DistrictCategory3D.vue'
import { fetchDistrictSummary, fetchCategoryStats } from '../api/index'
import { CATEGORY_COLOR_MAP, DEFAULT_CATEGORY_COLOR } from '../constants/categoryColors'

const selectedDistrict = ref('')
const districts = ref<Array<{ name: string; poi_count: number; pattern_count: number }>>([])
const categoryData = ref<Array<{ name: string; value: number }>>([])

const rankingChart = ref<HTMLDivElement | null>(null)
const categoryPieChart = ref<HTMLDivElement | null>(null)
let rankingChartInstance: echarts.ECharts | null = null
let categoryPieChartInstance: echarts.ECharts | null = null

const isAutoPlaying = ref(true)
const currentDistrictIndex = ref(0)
const progressPercent = ref(0)
let autoPlayTimer: number | null = null
let progressTimer: number | null = null
const AUTO_PLAY_INTERVAL = 5000
const PROGRESS_UPDATE_INTERVAL = 50

const totalPoiCount = computed(() => districts.value.reduce((sum, d) => sum + d.poi_count, 0))
const totalPatternCount = computed(() => districts.value.reduce((sum, d) => sum + d.pattern_count, 0))

const currentDistrictData = computed(() => {
  if (!selectedDistrict.value) return null
  return districts.value.find(d => d.name === selectedDistrict.value) || null
})

const poiPercentage = computed(() => {
  if (!currentDistrictData.value || totalPoiCount.value === 0) return '0.00'
  return ((currentDistrictData.value.poi_count / totalPoiCount.value) * 100).toFixed(2)
})

const patternPercentage = computed(() => {
  if (!currentDistrictData.value || totalPatternCount.value === 0) return '0.00'
  return ((currentDistrictData.value.pattern_count / totalPatternCount.value) * 100).toFixed(2)
})

function startAutoPlay() {
  if (districts.value.length === 0) return

  stopAutoPlay()

  progressPercent.value = 0
  progressTimer = window.setInterval(() => {
    progressPercent.value += (PROGRESS_UPDATE_INTERVAL / AUTO_PLAY_INTERVAL) * 100
    if (progressPercent.value >= 100) {
      progressPercent.value = 0
    }
  }, PROGRESS_UPDATE_INTERVAL)

  autoPlayTimer = window.setInterval(() => {
    currentDistrictIndex.value = (currentDistrictIndex.value + 1) % districts.value.length
    const district = districts.value[currentDistrictIndex.value]
    if (district) {
      selectedDistrict.value = district.name
    }
    progressPercent.value = 0
  }, AUTO_PLAY_INTERVAL)
}

function stopAutoPlay() {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    autoPlayTimer = null
  }
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

function toggleAutoPlay() {
  isAutoPlaying.value = !isAutoPlaying.value
  if (isAutoPlaying.value) {
    startAutoPlay()
  } else {
    stopAutoPlay()
  }
}

function jumpToDistrict(index: number) {
  currentDistrictIndex.value = index
  const district = districts.value[index]
  if (district) {
    selectedDistrict.value = district.name
  }
  progressPercent.value = 0
}

async function loadData() {
  try {
    const [districtSummary, categoryStats] = await Promise.all([
      fetchDistrictSummary(),
      fetchCategoryStats()
    ])

    districts.value = districtSummary.map(d => ({
      name: d.district,
      poi_count: d.poi_count,
      pattern_count: d.pattern_count
    }))

    categoryData.value = categoryStats.map(c => ({
      name: c.category_name,
      value: c.poi_count
    }))

    renderRankingChart()
    renderCategoryPieChart()

    if (districts.value.length > 0) {
      const firstDistrict = districts.value[0]
      if (firstDistrict) {
        selectedDistrict.value = firstDistrict.name
      }
      if (isAutoPlaying.value) {
        startAutoPlay()
      }
    }
  } catch (err) {
    console.error('加载数据失败:', err)
  }
}

function renderRankingChart() {
  if (!rankingChartInstance || !districts.value.length) return

  const sortedData = [...districts.value].sort((a, b) => b.pattern_count - a.pattern_count)

  rankingChartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff', fontSize: 12 },
      confine: true
    },
    grid: { left: 10, right: 30, top: 10, bottom: 10, containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } },
      axisLabel: { color: '#89a', fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: sortedData.map(d => d.name).reverse(),
      axisLabel: { color: '#fff', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } }
    },
    series: [{
      type: 'bar',
      data: sortedData.map(d => d.pattern_count).reverse(),
      barMaxWidth: 14,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(62, 229, 255, 0.1)' },
          { offset: 1, color: '#3EE5FF' }
        ]),
        borderRadius: [0, 4, 4, 0]
      }
    }]
  })
}

function renderCategoryPieChart() {
  if (!categoryPieChartInstance || !categoryData.value.length) return

  categoryPieChartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff', fontSize: 12 },
      confine: true
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 10,
      bottom: 10,
      textStyle: { color: '#fff', fontSize: 11 }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#060d18',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 12, fontWeight: 'bold', color: '#fff' }
      },
      data: categoryData.value.map(d => ({
        name: d.name,
        value: d.value,
        itemStyle: { color: CATEGORY_COLOR_MAP[d.name] || DEFAULT_CATEGORY_COLOR }
      }))
    }]
  })
}

watch(selectedDistrict, (newVal) => {
  const idx = districts.value.findIndex(d => d.name === newVal)
  if (idx !== -1) {
    currentDistrictIndex.value = idx
  }
})

onMounted(() => {
  if (rankingChart.value) {
    rankingChartInstance = echarts.init(rankingChart.value, 'dark')
  }
  if (categoryPieChart.value) {
    categoryPieChartInstance = echarts.init(categoryPieChart.value, 'dark')
  }

  loadData()

  window.addEventListener('resize', () => {
    rankingChartInstance?.resize()
    categoryPieChartInstance?.resize()
  })
})

onUnmounted(() => {
  stopAutoPlay()
  rankingChartInstance?.dispose()
  categoryPieChartInstance?.dispose()
})
</script>

<style scoped>
.districts-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #060d18;
  overflow: hidden;
}

.district-header {
  height: 64px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 18, 40, 0.6);
  border-bottom: 1px solid rgba(0, 200, 255, 0.2);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 20px;
  color: #fff;
  margin: 0;
}

.page-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.district-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.district-selector label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.selector {
  padding: 8px 16px;
  font-size: 14px;
  background: rgba(0, 18, 40, 0.8);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  min-width: 160px;
}

.selector option {
  background: #011428;
}

.content-area {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  min-height: 0;
}

.stats-panel {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #3EE5FF;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.chart {
  width: 100%;
  height: 100%;
}

.map-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.map-container {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(0, 200, 255, 0.3);
}

.district-map {
  width: 100%;
  height: 100%;
}

.chart-3d {
  height: 280px;
  flex-shrink: 0;
}

.category-panel {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.district-detail {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(0, 200, 255, 0.05);
  border-radius: 4px;
}

.detail-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.detail-value {
  font-size: 15px;
  font-weight: 600;
  color: #3EE5FF;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.carousel-btn {
  padding: 8px 12px;
  background: rgba(0, 18, 40, 0.8);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 6px;
  color: #3EE5FF;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.carousel-btn:hover {
  background: rgba(62, 229, 255, 0.1);
  border-color: rgba(0, 200, 255, 0.5);
}

.carousel-btn.active {
  background: rgba(62, 229, 255, 0.2);
  border-color: #3EE5FF;
}

.carousel-progress {
  height: 6px;
  background: rgba(0, 18, 40, 0.6);
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, rgba(62, 229, 255, 0.3), #3EE5FF);
  transition: width 0.05s linear;
}

.progress-labels {
  position: absolute;
  top: 8px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
}

.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(0, 200, 255, 0.3);
  cursor: pointer;
  transition: all 0.2s;
}

.progress-dot:hover {
  background: rgba(62, 229, 255, 0.6);
}

.progress-dot.active {
  background: #3EE5FF;
  box-shadow: 0 0 8px rgba(62, 229, 255, 0.6);
}
</style>
