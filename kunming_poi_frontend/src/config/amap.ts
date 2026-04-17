/**
 * 高德地图 JS API 全局配置
 * 从环境变量读取敏感配置，支持多环境部署
 * @author Hackerdallas
 */

// 高德 Web JS API Key（从环境变量读取）
export const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || ''

// 安全密钥（JS API 2.0 安全模式必填）
export const AMAP_SECRET = import.meta.env.VITE_AMAP_SECRET || ''

// 高德 JS API 版本
export const AMAP_VERSION = import.meta.env.VITE_AMAP_VERSION || '2.0'

// 开发环境检查
if (import.meta.env.DEV && (!AMAP_KEY || !AMAP_SECRET)) {
  console.warn(
    '[AMap] 缺少高德地图配置，请检查 .env.development 文件是否正确配置了 VITE_AMAP_KEY 和 VITE_AMAP_SECRET'
  )
}
