<script setup lang="ts">
/**
 * 模式筛选器面板
 * 支持按类别、FPI 阈值、阶数筛选模式
 * @author Hackerdallas
 */
import { ref, watch, computed, onMounted } from 'vue'
import { debounce } from 'lodash-es'
import { fetchCategoryStats, fetchFpiRanking, type CategoryStat, type PatternFilter, type FpiRankItem } from '@/api'

interface Props {
  modelValue?: PatternFilter
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
})

const emit = defineEmits<{
  (e: 'update:modelValue', filter: PatternFilter): void
  (e: 'filter-change', filter: PatternFilter): void
  (e: 'pattern-select', pattern: FpiRankItem): void
}>()

const categories = ref<CategoryStat[]>([])
const patterns = ref<FpiRankItem[]>([])
const loading = ref(false)
const selectedPatternId = ref<number | null>(null)

const selectedCategories = ref<string[]>([])
const fpiRange = ref<[number, number]>([0, 1])
const selectedLevels = ref<number[]>([])
const selectedDistrict = ref('')

const availableLevels = [2, 3, 4]

async function loadCategories() {
  try {
    loading.value = true
    categories.value = await fetchCategoryStats()
  } catch (e) {
    console.error('Failed to load categories:', e)
  } finally {
    loading.value = false
  }
}

async function loadPatterns() {
  try {
    loading.value = true
    patterns.value = await fetchFpiRanking(50)
    if (patterns.value.length > 0 && selectedPatternId.value === null) {
      const firstPattern = patterns.value[0]
      if (firstPattern) {
        selectPattern(firstPattern)
      }
    }
  } catch (e) {
    console.error('Failed to load patterns:', e)
  } finally {
    loading.value = false
  }
}

const currentFilter = computed<PatternFilter>(() => ({
  categories: selectedCategories.value.length > 0 ? selectedCategories.value : undefined,
  fpi_min: fpiRange.value[0] > 0 ? fpiRange.value[0] : undefined,
  fpi_max: fpiRange.value[1] < 1 ? fpiRange.value[1] : undefined,
  level: selectedLevels.value.length > 0 ? selectedLevels.value : undefined,
  district: selectedDistrict.value || undefined,
}))

const filteredPatterns = computed(() => {
  return patterns.value.filter(p => {
    if (currentFilter.value.fpi_min && p.fpi_score < currentFilter.value.fpi_min) return false
    if (currentFilter.value.fpi_max && p.fpi_score > currentFilter.value.fpi_max) return false
    if (currentFilter.value.level && p.pattern_level !== undefined && !currentFilter.value.level.includes(p.pattern_level)) return false
    return true
  })
})

const debouncedEmit = debounce(() => {
  emit('update:modelValue', currentFilter.value)
  emit('filter-change', currentFilter.value)
}, 300)

function toggleCategory(code: string) {
  const index = selectedCategories.value.indexOf(code)
  if (index === -1) {
    selectedCategories.value.push(code)
  } else {
    selectedCategories.value.splice(index, 1)
  }
  debouncedEmit()
}

function toggleLevel(level: number) {
  const index = selectedLevels.value.indexOf(level)
  if (index === -1) {
    selectedLevels.value.push(level)
  } else {
    selectedLevels.value.splice(index, 1)
  }
  debouncedEmit()
}

function resetFilters() {
  selectedCategories.value = []
  fpiRange.value = [0, 1]
  selectedLevels.value = []
  selectedDistrict.value = ''
  debouncedEmit()
}

function selectPattern(pattern: FpiRankItem) {
  selectedPatternId.value = pattern.pattern_id
  emit('pattern-select', pattern)
}

watch(
  [fpiRange, selectedDistrict],
  () => {
    debouncedEmit()
  },
  { deep: true }
)

onMounted(() => {
  loadCategories()
  loadPatterns()
})
</script>

<template>
  <div class="filter-panel">
    <!-- 模式列表 -->
    <div class="filter-section pattern-list-section">
      <div class="section-header">
        <span class="section-title">模式列表</span>
        <span class="section-count">共 {{ filteredPatterns.length }} 个</span>
      </div>
      <div class="pattern-list">
        <div
          v-for="pattern in filteredPatterns"
          :key="pattern.pattern_id"
          :class="['pattern-item', { active: selectedPatternId === pattern.pattern_id }]"
          @click="selectPattern(pattern)"
        >
          <div class="pattern-name">{{ pattern.pattern_name }}</div>
          <div class="pattern-meta">
            <span class="pattern-fpi">FPI: {{ pattern.fpi_score?.toFixed(4) }}</span>
            <span v-if="pattern.pattern_level" class="pattern-level">{{ pattern.pattern_level }}阶</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 类别筛选 -->
    <div class="filter-section">
      <div class="section-header">
        <span class="section-title">类别筛选</span>
        <span v-if="selectedCategories.length > 0" class="section-count">
          已选 {{ selectedCategories.length }} 项
        </span>
      </div>
      <div class="category-grid">
        <button
          v-for="cat in categories"
          :key="cat.category_code"
          :class="['category-btn', { active: selectedCategories.includes(cat.category_code) }]"
          :style="{
            '--cat-color': selectedCategories.includes(cat.category_code) ? '#3EE5FF' : 'rgba(0, 200, 255, 0.3)',
          }"
          @click="toggleCategory(cat.category_code)"
        >
          {{ cat.category_name.slice(0, 2) }}
        </button>
      </div>
    </div>

    <!-- FPI 范围筛选 -->
    <div class="filter-section">
      <div class="section-header">
        <span class="section-title">FPI 阈值</span>
        <span class="section-value">
          {{ fpiRange[0].toFixed(3) }} - {{ fpiRange[1].toFixed(3) }}
        </span>
      </div>
      <div class="range-slider">
        <input
          type="range"
          v-model.number="fpiRange[0]"
          :min="0"
          :max="fpiRange[1]"
          :step="0.001"
          class="slider slider-min"
        />
        <input
          type="range"
          v-model.number="fpiRange[1]"
          :min="fpiRange[0]"
          :max="1"
          :step="0.001"
          class="slider slider-max"
        />
      </div>
      <div class="range-labels">
        <span>0</span>
        <span>0.5</span>
        <span>1</span>
      </div>
    </div>

    <!-- 阶数筛选 -->
    <div class="filter-section">
      <div class="section-header">
        <span class="section-title">模式阶数</span>
      </div>
      <div class="level-buttons">
        <button
          v-for="level in availableLevels"
          :key="level"
          :class="['level-btn', { active: selectedLevels.includes(level) }]"
          @click="toggleLevel(level)"
        >
          {{ level }}阶
        </button>
      </div>
    </div>

    <!-- 重置按钮 -->
    <button class="reset-btn" @click="resetFilters">
      重置筛选
    </button>
  </div>
</template>

<style scoped>
.filter-panel {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-section {
  background: rgba(0, 18, 40, 0.5);
  border: 1px solid rgba(0, 200, 255, 0.2);
  border-radius: 6px;
  padding: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.section-count {
  font-size: 11px;
  color: #3EE5FF;
}

.section-value {
  font-size: 11px;
  color: #FFD700;
  font-family: monospace;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.category-btn {
  padding: 6px 4px;
  font-size: 11px;
  background: rgba(0, 18, 40, 0.6);
  border: 1px solid var(--cat-color);
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.category-btn:hover {
  background: rgba(62, 229, 255, 0.1);
}

.category-btn.active {
  background: rgba(62, 229, 255, 0.2);
  color: #3EE5FF;
}

.range-slider {
  position: relative;
  height: 24px;
}

.slider {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(0, 200, 255, 0.3);
  border-radius: 2px;
  outline: none;
  position: absolute;
  top: 10px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: #3EE5FF;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 6px rgba(62, 229, 255, 0.6);
}

.slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #3EE5FF;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 6px rgba(62, 229, 255, 0.6);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.level-buttons {
  display: flex;
  gap: 8px;
}

.level-btn {
  flex: 1;
  padding: 8px;
  font-size: 12px;
  background: rgba(0, 18, 40, 0.6);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.level-btn:hover {
  background: rgba(62, 229, 255, 0.1);
}

.level-btn.active {
  background: rgba(62, 229, 255, 0.2);
  border-color: #3EE5FF;
  color: #3EE5FF;
}

.reset-btn {
  width: 100%;
  padding: 10px;
  font-size: 12px;
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  border-radius: 4px;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: rgba(255, 107, 107, 0.3);
}

.pattern-list-section {
  max-height: 300px;
}

.pattern-list {
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pattern-list::-webkit-scrollbar {
  width: 4px;
}

.pattern-list::-webkit-scrollbar-track {
  background: rgba(0, 200, 255, 0.1);
  border-radius: 2px;
}

.pattern-list::-webkit-scrollbar-thumb {
  background: rgba(62, 229, 255, 0.4);
  border-radius: 2px;
}

.pattern-item {
  padding: 8px 10px;
  background: rgba(0, 18, 40, 0.6);
  border: 1px solid rgba(0, 200, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.pattern-item:hover {
  background: rgba(62, 229, 255, 0.1);
  border-color: rgba(0, 200, 255, 0.4);
}

.pattern-item.active {
  background: rgba(62, 229, 255, 0.15);
  border-color: #3EE5FF;
}

.pattern-name {
  font-size: 12px;
  color: #fff;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pattern-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.pattern-fpi {
  color: #FFD700;
}

.pattern-level {
  color: #3EE5FF;
}
</style>
