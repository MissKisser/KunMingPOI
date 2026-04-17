/**
 * 总览数据 Store
 * 管理 POI 总量、模式数、实例数、类别统计、行政区划统计
 * @author Hackerdallas
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchGlobalSummary,
  fetchCategoryStats,
  fetchDistrictSummary,
} from '@/api'
import type { CategoryStat, DistrictSummary } from '@/api'

export const useOverviewStore = defineStore('overview', () => {
  // ─── State ────────────────────────────────────────────────────────────────

  /** POI 总量 */
  const poiTotal = ref(0)
  /** 模式总数 */
  const patternTotal = ref(0)
  /** 实例总数 */
  const instanceTotal = ref(0)
  /** 类别统计 */
  const categoryStats = ref<CategoryStat[]>([])
  /** 行政区划统计 */
  const districtSummary = ref<DistrictSummary[]>([])
  /** 加载状态 */
  const loading = ref(false)
  /** 错误信息 */
  const error = ref<string | null>(null)

  // ─── Getters ──────────────────────────────────────────────────────────────

  /** 总览统计卡片数据 */
  const overviewStats = computed(() => [
    { label: 'POI 总量', value: poiTotal.value.toLocaleString() },
    { label: '挖掘模式数', value: patternTotal.value.toLocaleString() },
    { label: '模式实例数', value: instanceTotal.value.toLocaleString() },
  ])

  /** 饼图数据 */
  const pieData = computed(() =>
    categoryStats.value.map((c) => ({
      name: c.category_name,
      value: c.poi_count,
    }))
  )

  /** 类目数量 */
  const categoryCount = computed(() => categoryStats.value.length)

  /** 区域数量 */
  const districtCount = computed(() => districtSummary.value.length)

  // ─── Actions ──────────────────────────────────────────────────────────────

  /**
   * 获取所有总览数据
   */
  async function fetchAll() {
    loading.value = true
    error.value = null

    try {
      const [summaryRes, categoryRes, districtRes] = await Promise.all([
        fetchGlobalSummary(),
        fetchCategoryStats(),
        fetchDistrictSummary(),
      ])

      poiTotal.value = summaryRes.poi_total
      patternTotal.value = summaryRes.pattern_total
      instanceTotal.value = summaryRes.instance_total
      categoryStats.value = categoryRes
      districtSummary.value = districtRes
    } catch (err) {
      error.value = '数据加载失败'
      console.error('[OverviewStore] 获取数据失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  function reset() {
    poiTotal.value = 0
    patternTotal.value = 0
    instanceTotal.value = 0
    categoryStats.value = []
    districtSummary.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    poiTotal,
    patternTotal,
    instanceTotal,
    categoryStats,
    districtSummary,
    loading,
    error,
    // Getters
    overviewStats,
    pieData,
    categoryCount,
    districtCount,
    // Actions
    fetchAll,
    reset,
  }
})
