<!--
  模式分析独立页面
  深度分析空间同位模式，包含模式详情、演化树、关系网络
  @author Hackerdallas
-->
<template>
  <div class="patterns-view">
    <!-- 左侧：模式筛选面板 -->
    <aside class="filter-panel">
      <BasicContainer title="模式筛选" width="100%" height="100%">
        <PatternFilterPanel
          @filter-change="onFilterChange"
          @pattern-select="onPatternSelect"
        />
      </BasicContainer>
    </aside>

    <!-- 中间：模式详情展示 -->
    <main class="main-content">
      <!-- 模式详情卡片 -->
      <div class="pattern-detail" v-if="selectedPattern">
        <div class="detail-header">
          <h2 class="pattern-name">{{ selectedPattern.pattern_name }}</h2>
          <div class="pattern-stats">
            <div class="stat-item">
              <span class="stat-label">FPI 得分</span>
              <span class="stat-value">{{ selectedPattern.fpi_score?.toFixed(4) }}</span>
            </div>
          </div>
        </div>

        <!-- 模式组成类别 -->
        <div class="pattern-categories">
          <h3>模式组成</h3>
          <div class="category-tags">
            <span
              v-for="cat in patternCategories"
              :key="cat.name"
              class="category-tag"
              :style="{ backgroundColor: cat.color + '33', borderColor: cat.color, color: cat.color }"
            >
              {{ cat.name }}
            </span>
          </div>
        </div>

        <!-- 模式实例地图 -->
        <div class="pattern-map">
          <h3>空间分布</h3>
          <MapView ref="mapView" class="mini-map" />
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-else>
        <IconNetwork class="empty-icon" :size="64" color="rgba(255,255,255,0.3)" />
        <p>请从左侧选择一个模式进行分析</p>
      </div>
    </main>

    <!-- 右侧：模式演化与关系 -->
    <aside class="analysis-panel">
      <div class="panel-section">
        <BasicContainer title="模式演化树" width="100%" :height="280">
          <PatternEvolutionTree v-if="selectedPattern" :pattern-id="selectedPattern.pattern_id" />
          <div v-else class="empty-hint">选择模式查看演化路径</div>
        </BasicContainer>
      </div>

      <div class="panel-section">
        <BasicContainer title="关联模式网络" width="100%" :height="280">
          <PatternNetworkGraph height="240px" @pattern-click="onPatternClick" />
        </BasicContainer>
      </div>

      <div class="panel-section">
        <BasicContainer title="多阶模式统计" width="100%" :height="200">
          <LevelPatternStats />
        </BasicContainer>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BasicContainer from '../components/BasicContainer.vue'
import PatternFilterPanel from '../components/PatternFilterPanel.vue'
import PatternEvolutionTree from '../components/PatternEvolutionTree.vue'
import PatternNetworkGraph from '../components/PatternNetworkGraph.vue'
import LevelPatternStats from '../components/LevelPatternStats.vue'
import MapView from '../components/MapView.vue'
import { IconNetwork } from '../components/icons'
import { fetchFpiRanking, fetchPatternInstances } from '../api/index'
import type { FpiRankItem, PatternInstance } from '../api/index'
import { CATEGORY_COLOR_MAP, DEFAULT_CATEGORY_COLOR } from '../constants/categoryColors'

const selectedPattern = ref<FpiRankItem | null>(null)
const patternCategories = ref<Array<{ name: string; color: string }>>([])
const mapView = ref<InstanceType<typeof MapView> | null>(null)

function onFilterChange(filters: any) {
  console.log('Filter changed:', filters)
}

async function onPatternSelect(pattern: FpiRankItem) {
  selectedPattern.value = pattern
  await loadPatternDetail(pattern.pattern_id)
}

async function onPatternClick(patternId: number) {
  const data = await fetchFpiRanking(100)
  const pattern = data.find(p => p.pattern_id === patternId)
  if (pattern) {
    selectedPattern.value = pattern
    await loadPatternDetail(patternId)
  }
}

async function loadPatternDetail(patternId: number) {
  try {
    const instances: PatternInstance[] = await fetchPatternInstances(patternId)
    const categorySet = new Set<string>()
    instances.forEach(inst => {
      inst.pois.forEach(poi => categorySet.add(poi.category_name))
    })
    patternCategories.value = Array.from(categorySet).map(name => ({
      name,
      color: CATEGORY_COLOR_MAP[name] || DEFAULT_CATEGORY_COLOR
    }))
    mapView.value?.renderPattern(patternId)
  } catch (err) {
    console.error('加载模式详情失败:', err)
  }
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.patterns-view {
  width: 100%;
  height: 100%;
  display: flex;
  gap: 16px;
  padding: 16px;
  box-sizing: border-box;
  background: #060d18;
}

.filter-panel {
  width: 320px;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.pattern-detail {
  flex: 1;
  background: rgba(0, 18, 40, 0.6);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.pattern-name {
  font-size: 24px;
  color: #fff;
  margin: 0;
  font-weight: 600;
}

.pattern-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: rgba(0, 200, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(0, 200, 255, 0.2);
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #3EE5FF;
}

.pattern-categories h3,
.pattern-map h3 {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 12px 0;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 13px;
  border: 1px solid;
}

.pattern-map {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.mini-map {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
}

.empty-icon {
  margin-bottom: 16px;
}

.analysis-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-section {
  flex-shrink: 0;
}

.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}
</style>
