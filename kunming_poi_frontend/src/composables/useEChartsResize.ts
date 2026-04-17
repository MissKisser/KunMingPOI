/**
 * ECharts 图表实例统一 resize 管理
 * 使用 ResizeObserver 替代 window.resize，减少事件监听器数量
 * @author Hackerdallas
 */

import type { ECharts } from 'echarts'

// 全局图表实例注册表
const chartInstances = new Set<ECharts>()

// ResizeObserver 实例
let resizeObserver: ResizeObserver | null = null

// RAF ID 用于节流
let resizeRAF: number | null = null

/**
 * 初始化 ResizeObserver
 * 仅在首次注册图表时创建
 */
function initResizeObserver(): void {
  if (resizeObserver) return

  resizeObserver = new ResizeObserver(() => {
    // 使用 RAF 节流，避免高频重绘
    if (resizeRAF) {
      cancelAnimationFrame(resizeRAF)
    }
    resizeRAF = requestAnimationFrame(() => {
      chartInstances.forEach((chart) => {
        try {
          chart?.resize()
        } catch (e) {
          // 忽略已销毁的图表实例
        }
      })
    })
  })

  // 监听 body 尺寸变化
  resizeObserver.observe(document.body)
}

/**
 * 销毁 ResizeObserver
 * 当所有图表都注销时清理
 */
function destroyResizeObserver(): void {
  if (resizeObserver && chartInstances.size === 0) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (resizeRAF) {
    cancelAnimationFrame(resizeRAF)
    resizeRAF = null
  }
}

/**
 * ECharts resize 管理 Composable
 *
 * @example
 * ```typescript
 * import { useEChartsResize } from '@/composables/useEChartsResize'
 *
 * const { registerChart, unregisterChart } = useEChartsResize()
 *
 * onMounted(() => {
 *   chart = echarts.init(chartEl.value!, 'dark')
 *   registerChart(chart)
 * })
 *
 * onBeforeUnmount(() => {
 *   unregisterChart(chart)
 *   chart?.dispose()
 * })
 * ```
 */
export function useEChartsResize() {
  /**
   * 注册图表实例
   * @param chart ECharts 实例
   */
  function registerChart(chart: ECharts | null): void {
    if (!chart) return

    // 首次注册时初始化 ResizeObserver
    initResizeObserver()

    chartInstances.add(chart)
  }

  /**
   * 注销图表实例
   * @param chart ECharts 实例
   */
  function unregisterChart(chart: ECharts | null): void {
    if (!chart) return

    chartInstances.delete(chart)

    // 最后一个图表注销时清理 ResizeObserver
    destroyResizeObserver()
  }

  /**
   * 强制刷新所有图表
   */
  function resizeAll(): void {
    chartInstances.forEach((chart) => {
      try {
        chart?.resize()
      } catch (e) {
        // 忽略已销毁的图表实例
      }
    })
  }

  /**
   * 获取当前注册的图表数量
   */
  function getChartCount(): number {
    return chartInstances.size
  }

  return {
    registerChart,
    unregisterChart,
    resizeAll,
    getChartCount,
  }
}
