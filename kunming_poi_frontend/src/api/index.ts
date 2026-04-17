/**
 * Axios HTTP 客户端封装及接口定义
 * 支持请求缓存、错误处理、全局提示
 * @author Hackerdallas
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { requestCache, generateCacheKey } from '@/utils/cache'
import { useToast } from '@/composables/useToast'
import { API_CACHE_TTL, DEFAULT_CACHE_TTL } from '@/constants'

// ─── Axios 实例配置 ──────────────────────────────────────────────────────────

const http: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// ─── 响应拦截器：错误处理 ────────────────────────────────────────────────────

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const toast = useToast()

    // 获取错误信息
    let errorMessage = '网络请求失败，请稍后重试'

    if (error.response) {
      // 服务器返回错误
      const { status, data } = error.response
      if (data?.detail) {
        errorMessage = data.detail
      } else if (status === 401) {
        errorMessage = '未授权，请检查登录状态'
      } else if (status === 403) {
        errorMessage = '无权限访问'
      } else if (status === 404) {
        errorMessage = '请求的资源不存在'
      } else if (status >= 500) {
        errorMessage = '服务器错误，请稍后重试'
      }
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = '请求超时，请检查网络连接'
    } else if (error.message === 'Network Error') {
      errorMessage = '网络连接失败，请检查网络'
    }

    // 显示错误提示
    toast.error(errorMessage)

    return Promise.reject(error)
  }
)

// ─── 缓存请求封装 ────────────────────────────────────────────────────────────

/**
 * 带缓存的 GET 请求
 * @param url 请求路径
 * @param params 请求参数
 * @returns 响应数据
 */
async function cachedGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const cacheKey = generateCacheKey(url, params)

  // 尝试从缓存获取
  const cached = requestCache.get<T>(cacheKey)
  if (cached !== null) {
    return cached
  }

  // 发起请求
  const response: AxiosResponse<T> = await http.get<T>(url, { params })

  // 缓存响应数据
  const ttl = API_CACHE_TTL[url as keyof typeof API_CACHE_TTL] ?? DEFAULT_CACHE_TTL
  requestCache.set(cacheKey, response.data, ttl)

  return response.data
}

/**
 * 清除指定接口的缓存
 * @param urlPattern URL 匹配模式
 */
export function clearApiCache(urlPattern?: RegExp): void {
  if (urlPattern) {
    requestCache.clearPattern(urlPattern)
  } else {
    requestCache.clear()
  }
}

// ─── 接口类型定义 ──────────────────────────────────────────────────────────────

/** FPI 高频模式排行榜条目 */
export interface FpiRankItem {
  pattern_id: number
  pattern_name: string
  fpi_score: number
  pattern_level?: number
}

/** 汇总统计指标 */
export interface GlobalSummary {
  poi_total: number
  pattern_total: number
  instance_total: number
}

/** 分类统计 */
export interface CategoryStat {
  category_name: string
  category_code: string
  description: string
  poi_count: number
}

/** 模式空间坐标点 */
export interface PatternCoord {
  lng: number
  lat: number
}

/** POI详细信息（含类别） */
export interface PoiDetail {
  poi_id: number
  poi_name: string
  category_name: string
  lng: number
  lat: number
}

/** 模式实例数据 */
export interface PatternInstance {
  instance_id: number
  center_lng: number
  center_lat: number
  pois: PoiDetail[]
}

/** 热力图数据点 */
export interface HeatmapPoint {
  lng: number
  lat: number
}

/** 行政区划维度统计指标 */
export interface DistrictSummary {
  district: string
  poi_count: number
  pattern_count: number
}

/** 模式词云数据项 */
export interface WordCountItem {
  name: string
  value: number
}

/** POI 基础数据 */
export interface PoiData {
  id: number
  name: string
  category: string
  lng: number
  lat: number
}

// ─── Phase 1: 高阶模式挖掘可视化 ───────────────────────────────────────────────

/** 多阶模式统计 */
export interface LevelPatternStats {
  level: number
  pattern_count: number
  avg_fpi: number
  max_fpi: number
  top_patterns: FpiRankItem[]
}

/** 模式演化链节点 */
export interface PatternEvolution {
  pattern_id: number
  pattern_name: string
  level: number
  fpi_score: number
  parent_patterns: number[]
  child_patterns: number[]
}

/** 模式空间形态指标 */
export interface PatternMorphology {
  pattern_id: number
  instance_count: number
  metrics: {
    convex_hull_area: number
    avg_pair_distance: number
    std_pair_distance: number
    clustering_coefficient: number
    moran_index: number
    compactness: number
  }
  instances: {
    instance_id: number
    center: [number, number]
    member_pois: PoiDetail[]
  }[]
}

// ─── Phase 2: 空间关系深度分析 ─────────────────────────────────────────────────

/** 模式凸包数据 */
export interface PatternConvexHull {
  pattern_id: number
  hull_points: [number, number][]
  hull_area: number
  center: [number, number]
}

/** 核密度估计数据 */
export interface DensityEstimation {
  grid_size: [number, number]
  bounds: [[number, number], [number, number]]
  density_values: number[][]
  bandwidth: number
}

/** 模式实例聚类 */
export interface ClusteredInstances {
  pattern_id: number
  clusters: {
    cluster_id: number
    center: [number, number]
    instances: number[]
    count: number
  }[]
}

// ─── Phase 3: 高级图表 ─────────────────────────────────────────────────────────

/** 桑基图数据 */
export interface SankeyData {
  nodes: { name: string; depth: number }[]
  links: { source: string; target: string; value: number }[]
}

/** 模式关系网络 */
export interface PatternNetwork {
  nodes: { id: number; name: string; value: number; category: string }[]
  edges: { source: number; target: number; weight: number }[]
}

/** 区域×类别×模式数 3D 数据 */
export interface DistrictCategoryPattern3D {
  districts: string[]
  categories: string[]
  values: number[][]
}

// ─── Phase 4: 交互式探索 ───────────────────────────────────────────────────────

/** 模式筛选参数 */
export interface PatternFilter {
  categories?: string[]
  fpi_min?: number
  fpi_max?: number
  level?: number[]
  district?: string
  limit?: number
  offset?: number
}

/** 模式搜索结果 */
export interface PatternSearchResult {
  total: number
  patterns: FpiRankItem[]
}

/** 空间范围查询结果 */
export interface SpatialQueryResult {
  patterns: FpiRankItem[]
  poi_count: number
  density: number
}

/** 模式对比结果 */
export interface PatternComparison {
  patterns: PatternMorphology[]
  common_pois: PoiDetail[]
  similarity_matrix: number[][]
}

// ─── Phase 5: 时间序列扩展 ─────────────────────────────────────────────────────

/** 模式演化时间序列 */
export interface EvolutionTimeline {
  timestamps: string[]
  series: {
    pattern_id: number
    pattern_name: string
    fpi_values: number[]
    instance_counts: number[]
  }[]
}

// ─── 接口方法 ──────────────────────────────────────────────────────────────────

/** 获取 FPI 排行榜（Top N，默认 10） */
export const fetchFpiRanking = (limit = 10) =>
  cachedGet<FpiRankItem[]>('/fpi-ranking', { limit })

/** 获取指定模式下所有 POI 坐标 */
export const fetchPatternCoords = (patternId: number) =>
  cachedGet<PatternCoord[]>(`/pattern-coordinates/${patternId}`)

/** 获取指定模式的实例分组数据（含POI详情和类别） */
export const fetchPatternInstances = (patternId: number) =>
  cachedGet<PatternInstance[]>(`/pattern-instances/${patternId}`)

/** 获取POI热力图数据 */
export const fetchHeatmapData = (limit = 50000) =>
  cachedGet<HeatmapPoint[]>('/poi-heatmap-data', { limit })

/** 获取所有 POI 数据 */
export const fetchAllPoi = () => cachedGet<PoiData[]>('/all-pois')

/** 获取系统数据概览大盘 */
export const fetchGlobalSummary = () => cachedGet<GlobalSummary>('/global-summary')

/** 获取大类基础统计 */
export const fetchCategoryStats = () => cachedGet<CategoryStat[]>('/category-stats')

/** 获取行政区划汇总数据 */
export const fetchDistrictSummary = () => cachedGet<DistrictSummary[]>('/district-summary')

/** 获取高频模式类目词频统计 */
export const fetchPatternWordcloud = () => cachedGet<WordCountItem[]>('/pattern-wordcloud')

// ─── Phase 1: 高阶模式挖掘可视化 ───────────────────────────────────────────────

/** 获取多阶模式统计 */
export const fetchLevelPatternStats = () =>
  cachedGet<LevelPatternStats[]>('/level-pattern-stats')

/** 获取模式演化链 */
export const fetchPatternEvolution = (patternId: number) =>
  cachedGet<PatternEvolution>(`/pattern-evolution/${patternId}`)

/** 获取模式空间形态分析 */
export const fetchPatternMorphology = (patternId: number) =>
  cachedGet<PatternMorphology>(`/pattern-morphology/${patternId}`)

// ─── Phase 2: 空间关系深度分析 ─────────────────────────────────────────────────

/** 获取模式凸包数据 */
export const fetchPatternConvexHull = (patternId: number) =>
  cachedGet<PatternConvexHull>(`/pattern-convex-hull/${patternId}`)

/** 获取核密度估计数据 */
export const fetchDensityEstimation = (categoryId?: string, bandwidth?: number) =>
  cachedGet<DensityEstimation>('/density-estimation', { categoryId, bandwidth })

/** 获取模式实例聚类 */
export const fetchPatternClusters = (patternId: number, k = 5) =>
  cachedGet<ClusteredInstances>(`/pattern-clusters/${patternId}`, { k })

// ─── Phase 3: 高级图表 ─────────────────────────────────────────────────────────

/** 获取类别流向桑基图数据 */
export const fetchCategoryFlowSankey = () =>
  cachedGet<SankeyData>('/category-flow-sankey')

/** 获取模式关系网络数据 */
export const fetchPatternNetwork = (minWeight = 0.3) =>
  cachedGet<PatternNetwork>('/pattern-network', { minWeight })

/** 获取区域×类别×模式数 3D 数据 */
export const fetchDistrictCategoryPattern3D = () =>
  cachedGet<DistrictCategoryPattern3D>('/district-category-pattern-3d')

// ─── Phase 4: 交互式探索 ───────────────────────────────────────────────────────

/** 模式筛选搜索 */
export const searchPatterns = (filter: PatternFilter) =>
  cachedGet<PatternSearchResult>('/patterns/search', filter as Record<string, unknown>)

/** 空间范围查询 */
export const spatialQueryPatterns = async (polygon: [number, number][]): Promise<SpatialQueryResult> => {
  const response = await http.post<SpatialQueryResult>('/patterns/spatial-query', { polygon })
  return response.data
}

/** 模式对比分析 */
export const comparePatterns = async (patternIds: number[]): Promise<PatternComparison> => {
  const response = await http.post<PatternComparison>('/patterns/compare', { pattern_ids: patternIds })
  return response.data
}

// ─── Phase 5: 时间序列扩展 ─────────────────────────────────────────────────────

/** 获取模式演化时间序列 */
export const fetchEvolutionTimeline = (steps = 12, interval: 'month' | 'quarter' = 'month') =>
  cachedGet<EvolutionTimeline>('/evolution-timeline', { steps, interval })

export default http
