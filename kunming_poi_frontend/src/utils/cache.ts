/**
 * 请求缓存工具类
 * 用于缓存 API 响应数据，减少重复请求
 * @author Hackerdallas
 */

interface CacheItem<T> {
  /** 缓存数据 */
  data: T
  /** 缓存时间戳 */
  timestamp: number
  /** 缓存有效期（毫秒） */
  ttl: number
}

/**
 * 请求缓存管理器
 * 支持基于 URL 和参数的缓存，自动过期清理
 */
class RequestCache {
  private cache = new Map<string, CacheItem<unknown>>()

  /**
   * 获取缓存数据
   * @param key 缓存键名
   * @returns 缓存数据，不存在或已过期返回 null
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key) as CacheItem<T> | undefined

    if (!item) {
      return null
    }

    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  /**
   * 设置缓存数据
   * @param key 缓存键名
   * @param data 缓存数据
   * @param ttl 缓存有效期（毫秒），默认 60 秒
   */
  set<T>(key: string, data: T, ttl = 60000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    })
  }

  /**
   * 删除指定缓存
   * @param key 缓存键名
   */
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  /**
   * 按模式批量删除缓存
   * @param pattern 正则表达式模式
   */
  clearPattern(pattern: RegExp): void {
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 获取缓存数量
   */
  get size(): number {
    return this.cache.size
  }

  /**
   * 检查缓存是否存在且有效
   * @param key 缓存键名
   */
  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false

    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return false
    }

    return true
  }
}

/** 全局请求缓存实例 */
export const requestCache = new RequestCache()

/**
 * 生成缓存键
 * @param url 请求 URL
 * @param params 请求参数
 * @returns 缓存键
 */
export function generateCacheKey(url: string, params?: Record<string, unknown>): string {
  if (!params || Object.keys(params).length === 0) {
    return url
  }
  return `${url}:${JSON.stringify(params)}`
}
