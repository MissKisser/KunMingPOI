<script setup lang="ts">
/**
 * 多阶模式统计面板
 * 展示 2/3/4 阶模式的数量、平均 FPI、Top 模式
 * @author Hackerdallas
 */
import { ref, computed, onMounted } from 'vue'
import { fetchLevelPatternStats, type LevelPatternStats } from '@/api'
import CountUp from '@/components/CountUp.vue'
import Skeleton from '@/components/Skeleton.vue'

const loading = ref(true)
const error = ref<string | null>(null)
const levelStats = ref<LevelPatternStats[]>([])

const levelColors: Record<number, string> = {
  2: '#3EE5FF',
  3: '#4ECDC4',
  4: '#FF6B6B',
}

const levelLabels: Record<number, string> = {
  2: '二阶模式',
  3: '三阶模式',
  4: '四阶模式',
}

const totalPatterns = computed(() => {
  return levelStats.value.reduce((sum, s) => sum + s.pattern_count, 0)
})

const avgFpi = computed(() => {
  const total = totalPatterns.value
  if (total === 0) return 0
  const weightedSum = levelStats.value.reduce((sum, s) => sum + s.avg_fpi * s.pattern_count, 0)
  return weightedSum / total
})

async function loadData() {
  try {
    loading.value = true
    error.value = null
    levelStats.value = await fetchLevelPatternStats()
  } catch (e) {
    error.value = '加载失败'
    console.error('Failed to load level pattern stats:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

defineExpose({
  refresh: loadData,
})
</script>

<template>
  <div class="level-stats-panel">
    <Skeleton v-if="loading" variant="chart" />
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <div v-else class="stats-content">
      <!-- 总览卡片 -->
      <div class="overview-cards">
        <div class="overview-item">
          <span class="label">模式总数</span>
          <span class="value">
            <CountUp :end-val="totalPatterns" :duration="1500" />
          </span>
        </div>
        <div class="overview-item">
          <span class="label">平均 FPI</span>
          <span class="value highlight">{{ avgFpi.toFixed(4) }}</span>
        </div>
      </div>

      <!-- 各阶统计 -->
      <div class="level-cards">
        <div
          v-for="stat in levelStats"
          :key="stat.level"
          class="level-card"
          :style="{ '--level-color': levelColors[stat.level] || '#3EE5FF' }"
        >
          <div class="level-header">
            <span class="level-badge">{{ stat.level }}阶</span>
            <span class="level-label">{{ levelLabels[stat.level] }}</span>
          </div>
          <div class="level-metrics">
            <div class="metric">
              <span class="metric-value">
                <CountUp :end-val="stat.pattern_count" :duration="1200" />
              </span>
              <span class="metric-label">模式数</span>
            </div>
            <div class="metric">
              <span class="metric-value">{{ stat.avg_fpi.toFixed(4) }}</span>
              <span class="metric-label">平均 FPI</span>
            </div>
            <div class="metric">
              <span class="metric-value highlight">{{ stat.max_fpi.toFixed(4) }}</span>
              <span class="metric-label">最高 FPI</span>
            </div>
          </div>
          <!-- Top 模式列表 -->
          <div v-if="stat.top_patterns.length > 0" class="top-patterns">
            <div class="top-title">Top 模式</div>
            <div
              v-for="(pattern, idx) in stat.top_patterns.slice(0, 3)"
              :key="pattern.pattern_id"
              class="top-item"
            >
              <span class="rank">{{ idx + 1 }}</span>
              <span class="pattern-name">{{ pattern.pattern_name }}</span>
              <span class="pattern-fpi">{{ pattern.fpi_score.toFixed(4) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.level-stats-panel {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.stats-content {
  padding: 8px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.stats-content::-webkit-scrollbar {
  width: 4px;
}

.stats-content::-webkit-scrollbar-track {
  background: rgba(0, 200, 255, 0.1);
  border-radius: 2px;
}

.stats-content::-webkit-scrollbar-thumb {
  background: rgba(62, 229, 255, 0.4);
  border-radius: 2px;
}

.overview-cards {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.overview-item {
  flex: 1;
  background: rgba(0, 18, 40, 0.6);
  border: 1px solid rgba(0, 200, 255, 0.2);
  border-radius: 6px;
  padding: 10px;
  text-align: center;
}

.overview-item .label {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.overview-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #3EE5FF;
}

.overview-item .value.highlight {
  color: #FFD700;
}

.level-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-height: 0;
}

.level-card {
  background: rgba(0, 18, 40, 0.5);
  border: 1px solid var(--level-color);
  border-radius: 6px;
  padding: 10px;
  position: relative;
  overflow: hidden;
}

.level-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--level-color);
}

.level-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.level-badge {
  background: var(--level-color);
  color: #000;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 3px;
}

.level-label {
  font-size: 12px;
  color: #fff;
}

.level-metrics {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.metric {
  flex: 1;
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 14px;
  font-weight: bold;
  color: #fff;
}

.metric-value.highlight {
  color: #FFD700;
}

.metric-label {
  display: block;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.top-patterns {
  border-top: 1px solid rgba(0, 200, 255, 0.15);
  padding-top: 6px;
}

.top-title {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 0;
  font-size: 11px;
}

.top-item .rank {
  width: 14px;
  height: 14px;
  background: rgba(62, 229, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: #3EE5FF;
}

.top-item .pattern-name {
  flex: 1;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-item .pattern-fpi {
  color: #FFD700;
  font-weight: bold;
  font-size: 10px;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #ff6b6b;
  font-size: 14px;
}
</style>
