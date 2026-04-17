/**
 * 模式数据 Store
 * 管理 FPI 排行榜、词云数据
 * @author Hackerdallas
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchFpiRanking, fetchPatternWordcloud } from '@/api'
import type { FpiRankItem, WordCountItem } from '@/api'

export const usePatternsStore = defineStore('patterns', () => {
  // ─── State ────────────────────────────────────────────────────────────────

  /** FPI 排行榜数据 */
  const fpiRanking = ref<FpiRankItem[]>([])
  /** 词云数据 */
  const wordcloud = ref<WordCountItem[]>([])
  /** 加载状态 */
  const loading = ref(false)
  /** 错误信息 */
  const error = ref<string | null>(null)

  // ─── Actions ──────────────────────────────────────────────────────────────

  /**
   * 获取 FPI 排行榜
   * @param limit 返回数量，默认 10
   */
  async function fetchRanking(limit = 10) {
    loading.value = true
    error.value = null

    try {
      const data = await fetchFpiRanking(limit)
      fpiRanking.value = data
    } catch (err) {
      error.value = '排行榜数据加载失败'
      console.error('[PatternsStore] 获取排行榜失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取词云数据
   */
  async function fetchWordcloud() {
    loading.value = true
    error.value = null

    try {
      const data = await fetchPatternWordcloud()
      wordcloud.value = data
    } catch (err) {
      error.value = '词云数据加载失败'
      console.error('[PatternsStore] 获取词云失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取所有模式数据
   */
  async function fetchAll() {
    await Promise.all([fetchRanking(), fetchWordcloud()])
  }

  /**
   * 重置状态
   */
  function reset() {
    fpiRanking.value = []
    wordcloud.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    fpiRanking,
    wordcloud,
    loading,
    error,
    // Actions
    fetchRanking,
    fetchWordcloud,
    fetchAll,
    reset,
  }
})
