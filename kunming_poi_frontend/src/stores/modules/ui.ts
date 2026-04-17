/**
 * UI 状态 Store
 * 管理全局 UI 状态（加载、初始化等）
 * @author Hackerdallas
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // ─── State ────────────────────────────────────────────────────────────────

  /** 应用是否已初始化 */
  const initialized = ref(false)
  /** 全局加载状态 */
  const globalLoading = ref(false)
  /** 当前时间 */
  const currentTime = ref('')
  /** 定时器 ID */
  let timer: ReturnType<typeof setInterval> | null = null

  // ─── Actions ──────────────────────────────────────────────────────────────

  /**
   * 更新当前时间
   */
  function updateTime() {
    const now = new Date()
    currentTime.value = `${now.toLocaleDateString('zh-CN')} ${now.toLocaleTimeString('zh-CN', { hour12: false })}`
  }

  /**
   * 启动时间更新定时器
   */
  function startTimeUpdater() {
    updateTime()
    timer = setInterval(updateTime, 1000)
  }

  /**
   * 停止时间更新定时器
   */
  function stopTimeUpdater() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  /**
   * 设置初始化状态
   */
  function setInitialized(value: boolean) {
    initialized.value = value
  }

  /**
   * 设置全局加载状态
   */
  function setGlobalLoading(value: boolean) {
    globalLoading.value = value
  }

  /**
   * 重置状态
   */
  function reset() {
    stopTimeUpdater()
    initialized.value = false
    globalLoading.value = false
    currentTime.value = ''
  }

  return {
    // State
    initialized,
    globalLoading,
    currentTime,
    // Actions
    updateTime,
    startTimeUpdater,
    stopTimeUpdater,
    setInitialized,
    setGlobalLoading,
    reset,
  }
})
