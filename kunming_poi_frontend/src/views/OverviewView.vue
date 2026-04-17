<!--
  数据总览独立页面
  展示系统整体数据统计和摘要信息
  @author Hackerdallas
-->
<template>
  <div class="overview-view">
    <!-- 顶部统计卡片 -->
    <header class="stats-header">
      <div class="stat-card large">
        <div class="stat-icon">
          <IconLocation :size="32" color="#3EE5FF" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.poiCount.toLocaleString() }}</span>
          <span class="stat-label">POI 总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <IconLink :size="28" color="#4ECDC4" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.patternCount }}</span>
          <span class="stat-label">高频模式</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <IconNodes :size="28" color="#FF6B6B" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.instanceCount }}</span>
          <span class="stat-label">模式实例</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <IconRegion :size="28" color="#F7DC6F" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.districtCount }}</span>
          <span class="stat-label">行政区划</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <IconTag :size="28" color="#BB8FCE" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.categoryCount }}</span>
          <span class="stat-label">POI 类别</span>
        </div>
      </div>
      <div class="export-actions">
        <button class="export-btn" @click="handleExportCSV">
          <IconRefresh :size="14" color="#3EE5FF" />
          <span>导出 CSV</span>
        </button>
        <button class="export-btn" @click="handleExportJSON">
          <IconChart :size="14" color="#3EE5FF" />
          <span>导出 JSON</span>
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="content-grid">
      <!-- 左侧：类别分布 -->
      <div class="panel category-panel">
        <BasicContainer title="POI 类别分布" width="100%" height="100%">
          <div ref="categoryChart" class="chart" />
        </BasicContainer>
      </div>

      <!-- 中间：区域分布 -->
      <div class="panel district-panel">
        <BasicContainer title="区域 POI 分布" width="100%" height="100%">
          <div ref="districtChart" class="chart" />
        </BasicContainer>
      </div>

      <!-- 右侧：模式统计 -->
      <div class="panel pattern-panel">
        <BasicContainer title="模式阶数分布" width="100%" height="100%">
          <LevelPatternStats />
        </BasicContainer>
      </div>

      <!-- 底部：FPI 排行 -->
      <div class="panel ranking-panel">
        <BasicContainer title="FPI 排行榜 TOP 20" width="100%" height="100%">
          <FpiRanking :limit="20" @pattern-click="onPatternClick" />
        </BasicContainer>
      </div>

      <!-- 底部：桑基图 -->
      <div class="panel sankey-panel">
        <BasicContainer title="类别关联流向" width="100%" height="100%">
          <SankeyFlowChart height="100%" />
        </BasicContainer>
      </div>

      <!-- 底部：时间演化 -->
      <div class="panel timeline-panel">
        <BasicContainer title="模式演化时序" width="100%" height="100%">
          <EvolutionTimeline height="100%" />
        </BasicContainer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import * as echarts from 'echarts'
import BasicContainer from '../components/BasicContainer.vue'
import LevelPatternStats from '../components/LevelPatternStats.vue'
import FpiRanking from '../components/FpiRanking.vue'
import SankeyFlowChart from '../components/SankeyFlowChart.vue'
import EvolutionTimeline from '../components/EvolutionTimeline.vue'
import { IconLocation, IconLink, IconNodes, IconRegion, IconTag, IconRefresh, IconChart } from '../components/icons'
import { fetchGlobalSummary, fetchCategoryStats, fetchDistrictSummary, fetchFpiRanking } from '../api/index'
import { CATEGORY_COLOR_MAP, DEFAULT_CATEGORY_COLOR } from '../constants/categoryColors'
import { exportToCSV, exportToJSON, formatDateTimeForFilename } from '../utils/export'

const categoryChart = ref<HTMLDivElement | null>(null)
const districtChart = ref<HTMLDivElement | null>(null)
let categoryChartInstance: echarts.ECharts | null = null
let districtChartInstance: echarts.ECharts | null = null

const animatedStats = reactive({
  poiCount: 0,
  patternCount: 0,
  instanceCount: 0,
  districtCount: 0,
  categoryCount: 0
})

const targetStats = reactive({
  poiCount: 0,
  patternCount: 0,
  instanceCount: 0,
  districtCount: 0,
  categoryCount: 0
})

function animateNumbers() {
  const duration = 1500
  const startTime = Date.now()

  function update() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeProgress = 1 - Math.pow(1 - progress, 3)

    animatedStats.poiCount = Math.floor(targetStats.poiCount * easeProgress)
    animatedStats.patternCount = Math.floor(targetStats.patternCount * easeProgress)
    animatedStats.instanceCount = Math.floor(targetStats.instanceCount * easeProgress)
    animatedStats.districtCount = Math.floor(targetStats.districtCount * easeProgress)
    animatedStats.categoryCount = Math.floor(targetStats.categoryCount * easeProgress)

    if (progress < 1) {
      requestAnimationFrame(update)
    }
  }

  update()
}

async function loadData() {
  try {
    const [summary, categoryStats, districtStats] = await Promise.all([
      fetchGlobalSummary(),
      fetchCategoryStats(),
      fetchDistrictSummary()
    ])

    targetStats.poiCount = summary.poi_total || 0
    targetStats.patternCount = summary.pattern_total || 0
    targetStats.instanceCount = summary.instance_total || 0
    targetStats.districtCount = districtStats.length
    targetStats.categoryCount = categoryStats.length

    animateNumbers()

    renderCategoryChart(categoryStats)
    renderDistrictChart(districtStats)
  } catch (err) {
    console.error('加载数据失败:', err)
  }
}

function renderCategoryChart(data: Array<{ category_name: string; poi_count: number }>) {
  if (!categoryChartInstance) return

  const sortedData = [...data].sort((a, b) => b.poi_count - a.poi_count)

  categoryChartInstance.setOption({
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
      right: 20,
      top: 'center',
      textStyle: { color: '#fff', fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#060d18',
        borderWidth: 3
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' }
      },
      data: sortedData.map(d => ({
        name: d.category_name,
        value: d.poi_count,
        itemStyle: { color: CATEGORY_COLOR_MAP[d.category_name] || DEFAULT_CATEGORY_COLOR }
      }))
    }]
  })
}

function renderDistrictChart(data: Array<{ district: string; poi_count: number; pattern_count: number }>) {
  if (!districtChartInstance) return

  const sortedData = [...data].sort((a, b) => b.poi_count - a.poi_count)

  districtChartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(6, 20, 38, 0.9)',
      borderColor: '#3EE5FF',
      textStyle: { color: '#fff', fontSize: 12 },
      confine: true
    },
    legend: {
      data: ['POI 数量', '模式数量'],
      textStyle: { color: '#fff', fontSize: 12 },
      top: 10
    },
    grid: { left: 10, right: 20, top: 50, bottom: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: sortedData.map(d => d.district),
      axisLabel: { color: '#fff', fontSize: 11, rotate: 30 },
      axisLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.2)' } }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 200, 255, 0.1)', type: 'dashed' } },
      axisLabel: { color: '#89a', fontSize: 10 }
    },
    series: [
      {
        name: 'POI 数量',
        type: 'bar',
        data: sortedData.map(d => d.poi_count),
        barMaxWidth: 20,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3EE5FF' },
            { offset: 1, color: 'rgba(62, 229, 255, 0.2)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '模式数量',
        type: 'bar',
        data: sortedData.map(d => d.pattern_count),
        barMaxWidth: 20,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#FF6B6B' },
            { offset: 1, color: 'rgba(255, 107, 107, 0.2)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  })
}

function onPatternClick(patternId: number) {
  console.log('Pattern clicked:', patternId)
}

async function handleExportCSV() {
  try {
    const [categoryStats, districtStats, rankingData] = await Promise.all([
      fetchCategoryStats(),
      fetchDistrictSummary(),
      fetchFpiRanking(100)
    ])

    const timestamp = formatDateTimeForFilename()

    exportToCSV(categoryStats, `昆明POI类别统计_${timestamp}`, [
      { key: 'category_name', label: '类别名称' },
      { key: 'category_code', label: '类别编码' },
      { key: 'poi_count', label: 'POI数量' }
    ])

    exportToCSV(districtStats, `昆明区域统计_${timestamp}`, [
      { key: 'district', label: '行政区划' },
      { key: 'poi_count', label: 'POI数量' },
      { key: 'pattern_count', label: '模式数量' }
    ])

    exportToCSV(rankingData, `昆明FPI排行榜_${timestamp}`, [
      { key: 'pattern_id', label: '模式ID' },
      { key: 'pattern_name', label: '模式名称' },
      { key: 'fpi_score', label: 'FPI得分' }
    ])
  } catch (err) {
    console.error('导出失败:', err)
  }
}

async function handleExportJSON() {
  try {
    const [summary, categoryStats, districtStats, rankingData] = await Promise.all([
      fetchGlobalSummary(),
      fetchCategoryStats(),
      fetchDistrictSummary(),
      fetchFpiRanking(100)
    ])

    const timestamp = formatDateTimeForFilename()
    const exportData = {
      exportTime: new Date().toISOString(),
      summary: {
        poiTotal: summary.poi_total,
        patternTotal: summary.pattern_total,
        instanceTotal: summary.instance_total
      },
      categoryStats,
      districtStats,
      fpiRanking: rankingData
    }

    exportToJSON(exportData, `昆明POI数据总览_${timestamp}`)
  } catch (err) {
    console.error('导出失败:', err)
  }
}

onMounted(() => {
  if (categoryChart.value) {
    categoryChartInstance = echarts.init(categoryChart.value, 'dark')
  }
  if (districtChart.value) {
    districtChartInstance = echarts.init(districtChart.value, 'dark')
  }

  loadData()

  window.addEventListener('resize', () => {
    categoryChartInstance?.resize()
    districtChartInstance?.resize()
  })
})
</script>

<style scoped>
.overview-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #060d18;
  overflow: hidden;
}

.stats-header {
  height: 100px;
  padding: 16px 24px;
  display: flex;
  gap: 16px;
  background: rgba(0, 18, 40, 0.6);
  border-bottom: 1px solid rgba(0, 200, 255, 0.2);
  flex-shrink: 0;
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(0, 200, 255, 0.05);
  border: 1px solid rgba(0, 200, 255, 0.2);
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  background: rgba(0, 200, 255, 0.1);
  border-color: rgba(0, 200, 255, 0.4);
}

.stat-card.large {
  flex: 1.5;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: rgba(62, 229, 255, 0.1);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #3EE5FF;
  font-family: 'MiSans-Demibold', sans-serif;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.export-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  background: rgba(0, 200, 255, 0.1);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 6px;
  color: #3EE5FF;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  background: rgba(0, 200, 255, 0.2);
  border-color: rgba(0, 200, 255, 0.5);
}

.btn-icon {
  font-size: 14px;
}

.content-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: minmax(220px, 1fr) minmax(300px, 1fr);
  gap: 16px;
  padding: 16px;
  min-height: 0;
  overflow: hidden;
}

.panel {
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel :deep(.basic-container) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel :deep(.container-body) {
  flex: 1;
  min-height: 0;
}

.panel :deep(.container-main) {
  height: 100%;
  min-height: 0;
  overflow: auto;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 180px;
}
</style>
