/**
 * ECharts 自动轮播 Composable
 * 为 ECharts 实例提供自动高亮、取消高亮及显示提示框的轮播功能
 * @author Hackerdallas
 */
import { ref, onBeforeUnmount } from 'vue'
import type { ECharts } from 'echarts'

interface AutoCarouselOptions {
  interval?: number // 轮播间隔时间，默认 3000ms
}

export function useEChartsAutoCarousel(options: AutoCarouselOptions = {}) {
  const { interval = 3000 } = options
  const timer = ref<ReturnType<typeof setInterval> | null>(null)
  const currentIndex = ref(-1)
  // 持有实例引用，供 globalout 回调中重启轮播
  let chartRef: ECharts | null = null
  let dataLenRef = 0

  /**
   * 启动轮播
   * @param chart ECharts 实例
   * @param dataLen 数据长度
   */
  const startRotation = (chart: ECharts | null, dataLen: number) => {
    if (!chart || dataLen <= 0) return

    // 更新实例引用
    chartRef = chart
    dataLenRef = dataLen

    stopRotation()

    timer.value = setInterval(() => {
      // 取消上一个高亮
      if (currentIndex.value >= 0) {
        chart.dispatchAction({
          type: 'downplay',
          seriesIndex: 0,
          dataIndex: currentIndex.value
        })
      }

      // 计算下一个索引
      currentIndex.value = (currentIndex.value + 1) % dataLen

      // 触发当前索引的高亮与 Tooltip
      chart.dispatchAction({
        type: 'highlight',
        seriesIndex: 0,
        dataIndex: currentIndex.value
      })
      chart.dispatchAction({
        type: 'showTip',
        seriesIndex: 0,
        dataIndex: currentIndex.value
      })
    }, interval)

    // 使用 ECharts 自身事件系统实现悬停暂停
    // mouseover：鼠标进入任意数据项区域时触发
    // globalout：鼠标离开整个图表区域时触发
    chart.off('mouseover', stopRotation)
    chart.on('mouseover', stopRotation)
    chart.off('globalout', _onGlobalOut)
    chart.on('globalout', _onGlobalOut)
  }

  /**
   * 停止轮播
   */
  const stopRotation = () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  /**
   * 鼠标离开图表整体区域时的回调，负责重启轮播
   */
  const _onGlobalOut = () => {
    startRotation(chartRef, dataLenRef)
  }

  onBeforeUnmount(stopRotation)

  return {
    startRotation,
    stopRotation
  }
}
