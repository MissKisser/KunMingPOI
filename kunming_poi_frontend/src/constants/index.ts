/**
 * 全局常量配置
 * 统一管理所有魔法值，便于维护和主题定制
 * @author Hackerdallas
 */

// ─── 热力图配置 ──────────────────────────────────────────────────────────────
export const HEATMAP_CONFIG = {
  /** 热力点半径 */
  RADIUS: 25,
  /** 透明度范围 [最小, 最大] */
  OPACITY: [0, 0.8] as [number, number],
  /** 热力值上限 */
  MAX_COUNT: 20,
  /** 默认数据加载量 */
  DATA_LIMIT: 50000,
  /** 首屏快速加载量 */
  INITIAL_LOAD_LIMIT: 10000,
  /** 缩放级别范围 */
  ZOOMS: [3, 20] as [number, number],
  /** Z-index */
  Z_INDEX: 130,
  /** 渐变色配置 */
  GRADIENT: {
    0.1: 'rgba(0, 100, 255, 0.4)',
    0.3: 'rgba(0, 200, 255, 0.6)',
    0.5: 'rgba(0, 255, 200, 0.75)',
    0.7: 'rgba(255, 255, 0, 0.85)',
    1.0: 'rgba(255, 80, 0, 1)',
  },
} as const

// ─── 轮播配置 ────────────────────────────────────────────────────────────────
export const CAROUSEL_CONFIG = {
  /** 自动轮播间隔（毫秒） */
  INTERVAL: 3000,
} as const

// ─── 地图配置 ────────────────────────────────────────────────────────────────
export const MAP_CONFIG = {
  /** 昆明市中心坐标 */
  CENTER: [102.7184, 25.0406] as [number, number],
  /** 初始缩放级别（直接显示昆明市范围） */
  INITIAL_ZOOM: 10,
  /** 目标缩放级别 */
  TARGET_ZOOM: 9.5,
  /** 飞入动画持续时间（毫秒） */
  FLY_DURATION: 2000,
  /** 俯仰角动画持续时间（毫秒） */
  PITCH_DURATION: 800,
  /** 目标俯仰角 */
  TARGET_PITCH: 30,
  /** 看板展开等待时间（毫秒） */
  HEADER_DELAY: 100,
  /** 等待看板展开时间（毫秒） */
  WAIT_FOR_HEADER: 500,
} as const

// ─── ECharts 通用配置 ────────────────────────────────────────────────────────
export const ECHARTS_THEME = {
  /** Tooltip 背景色 */
  TOOLTIP_BG: 'rgba(6, 20, 38, 0.8)',
  /** Tooltip 边框色 */
  TOOLTIP_BORDER: '#3EE5FF',
  /** 基础 Grid 配置 */
  GRID_BASE: { left: 10, right: 30, top: 10, bottom: 0, containLabel: true },
  /** 带底部边距的 Grid 配置 */
  GRID_WITH_BOTTOM: { left: 8, right: 30, top: 10, bottom: 8, containLabel: true },
  /** 分割线颜色 */
  SPLIT_LINE: 'rgba(0, 200, 255, 0.1)',
  /** 轴标签颜色 */
  AXIS_LABEL_COLOR: '#89a',
  /** 轴标签字号 */
  AXIS_LABEL_FONT_SIZE: 10,
  /** Y 轴标签颜色 */
  Y_AXIS_LABEL_COLOR: '#fff',
  /** Y 轴标签字号 */
  Y_AXIS_LABEL_FONT_SIZE: 11,
  /** Y 轴线颜色 */
  Y_AXIS_LINE_COLOR: 'rgba(0, 200, 255, 0.2)',
  /** 柱状图渐变色起始 */
  BAR_GRADIENT_START: 'rgba(62, 229, 255, 0.1)',
  /** 柱状图渐变色结束 */
  BAR_GRADIENT_END: '#3EE5FF',
  /** 柱状图最大宽度 */
  BAR_MAX_WIDTH: 16,
  /** 柱状图圆角 */
  BAR_BORDER_RADIUS: [0, 4, 4, 0] as [number, number, number, number],
  /** 柱状图阴影模糊 */
  BAR_SHADOW_BLUR: 10,
  /** 柱状图阴影颜色 */
  BAR_SHADOW_COLOR: 'rgba(62, 229, 255, 0.4)',
  /** 高亮颜色 */
  EMPHASIS_COLOR: '#00e5ff',
  /** 高亮阴影模糊 */
  EMPHASIS_SHADOW_BLUR: 20,
} as const

// ─── 散点图配置 ──────────────────────────────────────────────────────────────
export const SCATTER_CONFIG = {
  /** Z-index */
  Z_INDEX: 10,
  /** 透明度 */
  OPACITY: 0.85,
  /** 缩放级别范围 */
  ZOOMS: [2, 22] as [number, number],
  /** 散点大小 */
  SIZE: [12, 12] as [number, number],
  /** 边框宽度 */
  BORDER_WIDTH: 2,
  /** 边框颜色 */
  BORDER_COLOR: 'rgba(255, 255, 255, 0.6)',
} as const

// ─── API 缓存配置 ────────────────────────────────────────────────────────────
export const API_CACHE_TTL = {
  /** 总览数据缓存时间（毫秒） */
  '/global-summary': 60000,
  /** 类别统计缓存时间 */
  '/category-stats': 60000,
  /** 行政区划缓存时间 */
  '/district-summary': 60000,
  /** FPI 排行缓存时间 */
  '/fpi-ranking': 30000,
  /** 词云缓存时间 */
  '/pattern-wordcloud': 30000,
  /** 热力图数据缓存时间 */
  '/poi-heatmap-data': 300000,
} as const

// ─── 默认缓存时间 ────────────────────────────────────────────────────────────
export const DEFAULT_CACHE_TTL = 60000

// ─── 地图样式配置 ────────────────────────────────────────────────────────────
export const MAP_STYLE_OPTIONS = [
  { key: 'dark', label: '暗黑', style: 'amap://styles/dark' },
  { key: 'darkblue', label: '深蓝暗色', style: 'amap://styles/darkblue' },
  { key: 'blue', label: '深蓝科技', style: 'amap://styles/blue' },
  { key: 'normal', label: '标准', style: 'amap://styles/normal' },
  { key: 'satellite', label: '卫星图', style: 'satellite' },
] as const

// ─── LocalStorage 键名 ──────────────────────────────────────────────────────
export const STORAGE_KEYS = {
  /** 地图样式偏好 */
  MAP_STYLE: 'mapStyleKey',
} as const
