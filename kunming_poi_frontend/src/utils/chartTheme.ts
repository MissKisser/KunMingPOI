/**
 * ECharts 统一主题配置
 * 保持所有图表视觉风格一致
 * @author Hackerdallas
 */

import * as echarts from 'echarts'

export const CHART_THEME = {
  // 背景色
  backgroundColor: 'transparent',

  // 调色板
  color: [
    '#3EE5FF',
    '#4fc8ff',
    '#00e5ff',
    '#FF6B6B',
    '#4ECDC4',
    '#45B7D1',
    '#FFA07A',
    '#98D8C8',
    '#F7DC6F',
    '#BB8FCE',
  ],

  // 标题样式
  title: {
    textStyle: {
      color: '#fff',
      fontSize: 16,
      fontWeight: 600,
    },
    subtextStyle: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 12,
    },
  },

  // 图例样式
  legend: {
    textStyle: {
      color: '#fff',
      fontSize: 12,
    },
    pageTextStyle: {
      color: '#fff',
    },
    pageIconColor: '#3EE5FF',
    pageIconInactiveColor: 'rgba(62, 229, 255, 0.3)',
  },

  // 提示框样式
  tooltip: {
    backgroundColor: 'rgba(6, 20, 38, 0.9)',
    borderColor: '#3EE5FF',
    borderWidth: 1,
    textStyle: {
      color: '#fff',
      fontSize: 12,
    },
    confine: true,
  },

  // 坐标轴样式
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.2)',
      },
    },
    axisTick: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.2)',
      },
    },
    axisLabel: {
      color: '#fff',
      fontSize: 11,
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.1)',
        type: 'dashed' as const,
      },
    },
  },

  valueAxis: {
    axisLine: {
      show: false,
    },
    axisTick: {
      show: false,
    },
    axisLabel: {
      color: '#89a',
      fontSize: 10,
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.1)',
        type: 'dashed' as const,
      },
    },
  },

  // 时间轴样式
  timeAxis: {
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.2)',
      },
    },
    axisTick: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.2)',
      },
    },
    axisLabel: {
      color: '#fff',
      fontSize: 11,
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 200, 255, 0.1)',
        type: 'dashed' as const,
      },
    },
  },
}

/**
 * 柱状图渐变色配置
 */
export function createBarGradient(
  _chart: echarts.ECharts,
  startColor = 'rgba(62, 229, 255, 0.1)',
  endColor = '#3EE5FF'
) {
  return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
    { offset: 0, color: startColor },
    { offset: 1, color: endColor },
  ])
}

/**
 * 垂直柱状图渐变色配置
 */
export function createVerticalBarGradient(
  _chart: echarts.ECharts,
  startColor = 'rgba(62, 229, 255, 0.1)',
  endColor = '#3EE5FF'
) {
  return new echarts.graphic.LinearGradient(0, 1, 0, 0, [
    { offset: 0, color: startColor },
    { offset: 1, color: endColor },
  ])
}

/**
 * 注册自定义主题
 */
export function registerCustomTheme() {
  echarts.registerTheme('kunming-dark', CHART_THEME)
}
