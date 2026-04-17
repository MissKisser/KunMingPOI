/**
 * 地图状态 Store
 * 管理当前选中模式、图层可见性、类别筛选
 * @author Hackerdallas
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchPatternInstances } from '@/api'
import type { PatternInstance } from '@/api'

export const useMapStore = defineStore('map', () => {
  // ─── State ────────────────────────────────────────────────────────────────

  /** 当前选中的模式 ID */
  const currentPatternId = ref<number | null>(null)
  /** 当前模式的实例数据 */
  const currentInstances = ref<PatternInstance[]>([])
  /** 图层可见性 */
  const layerVisibility = ref({
    heatmap: true,
    scatter: true,
  })
  /** 类别可见性 */
  const categoryVisibility = ref<Record<string, boolean>>({})
  /** 加载状态 */
  const loading = ref(false)
  /** 错误信息 */
  const error = ref<string | null>(null)

  // ─── Actions ──────────────────────────────────────────────────────────────

  /**
   * 加载指定模式的数据
   * @param patternId 模式 ID
   */
  async function loadPattern(patternId: number) {
    if (currentPatternId.value === patternId) {
      return // 已加载相同模式，跳过
    }

    loading.value = true
    error.value = null
    currentPatternId.value = patternId

    try {
      const instances = await fetchPatternInstances(patternId)
      currentInstances.value = instances

      // 初始化类别可见性
      instances.forEach((inst) => {
        inst.pois.forEach((poi) => {
          if (categoryVisibility.value[poi.category_name] === undefined) {
            categoryVisibility.value[poi.category_name] = true
          }
        })
      })
    } catch (err) {
      error.value = '模式数据加载失败'
      console.error('[MapStore] 加载模式失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除当前模式
   */
  function clearPattern() {
    currentPatternId.value = null
    currentInstances.value = []
    categoryVisibility.value = {}
  }

  /**
   * 切换图层可见性
   * @param layer 图层名称
   */
  function toggleLayer(layer: 'heatmap' | 'scatter') {
    layerVisibility.value[layer] = !layerVisibility.value[layer]
  }

  /**
   * 设置图层可见性
   * @param layer 图层名称
   * @param visible 可见性
   */
  function setLayerVisibility(layer: 'heatmap' | 'scatter', visible: boolean) {
    layerVisibility.value[layer] = visible
  }

  /**
   * 切换类别可见性
   * @param categoryName 类别名称
   */
  function toggleCategory(categoryName: string) {
    categoryVisibility.value[categoryName] = !categoryVisibility.value[categoryName]
  }

  /**
   * 设置类别可见性
   * @param categoryName 类别名称
   * @param visible 可见性
   */
  function setCategoryVisibility(categoryName: string, visible: boolean) {
    categoryVisibility.value[categoryName] = visible
  }

  /**
   * 显示所有类别
   */
  function showAllCategories() {
    Object.keys(categoryVisibility.value).forEach((name) => {
      categoryVisibility.value[name] = true
    })
  }

  /**
   * 隐藏所有类别
   */
  function hideAllCategories() {
    Object.keys(categoryVisibility.value).forEach((name) => {
      categoryVisibility.value[name] = false
    })
  }

  /**
   * 重置状态
   */
  function reset() {
    currentPatternId.value = null
    currentInstances.value = []
    layerVisibility.value = { heatmap: true, scatter: true }
    categoryVisibility.value = {}
    loading.value = false
    error.value = null
  }

  return {
    // State
    currentPatternId,
    currentInstances,
    layerVisibility,
    categoryVisibility,
    loading,
    error,
    // Actions
    loadPattern,
    clearPattern,
    toggleLayer,
    setLayerVisibility,
    toggleCategory,
    setCategoryVisibility,
    showAllCategories,
    hideAllCategories,
    reset,
  }
})
