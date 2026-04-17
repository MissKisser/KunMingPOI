import { describe, it, expect, beforeEach } from 'vitest'
import { requestCache, generateCacheKey } from '../cache'

describe('RequestCache', () => {
  beforeEach(() => {
    requestCache.clear()
  })

  it('should set and get cache', () => {
    const key = 'test-key'
    const data = { name: 'test', value: 123 }

    requestCache.set(key, data)
    const result = requestCache.get<typeof data>(key)

    expect(result).toEqual(data)
  })

  it('should return null for non-existent key', () => {
    const result = requestCache.get('non-existent')
    expect(result).toBeNull()
  })

  it('should return null for expired cache', () => {
    const key = 'expired-key'
    const data = { name: 'test' }

    // 设置 1ms 过期时间
    requestCache.set(key, data, 1)

    // 等待过期
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        const result = requestCache.get<typeof data>(key)
        expect(result).toBeNull()
        resolve()
      }, 10)
    })
  })

  it('should delete cache by key', () => {
    const key = 'delete-key'
    requestCache.set(key, { data: 'test' })

    const deleted = requestCache.delete(key)
    expect(deleted).toBe(true)
    expect(requestCache.get(key)).toBeNull()
  })

  it('should clear cache by pattern', () => {
    requestCache.set('api:user:1', { id: 1 })
    requestCache.set('api:user:2', { id: 2 })
    requestCache.set('api:post:1', { id: 1 })

    requestCache.clearPattern(/^api:user/)

    expect(requestCache.get('api:user:1')).toBeNull()
    expect(requestCache.get('api:user:2')).toBeNull()
    expect(requestCache.get('api:post:1')).not.toBeNull()
  })

  it('should check if cache exists', () => {
    const key = 'exists-key'
    requestCache.set(key, { data: 'test' })

    expect(requestCache.has(key)).toBe(true)
    expect(requestCache.has('non-existent')).toBe(false)
  })

  it('should return cache size', () => {
    expect(requestCache.size).toBe(0)

    requestCache.set('key1', { data: 1 })
    requestCache.set('key2', { data: 2 })

    expect(requestCache.size).toBe(2)
  })
})

describe('generateCacheKey', () => {
  it('should return url when no params', () => {
    const key = generateCacheKey('/api/test')
    expect(key).toBe('/api/test')
  })

  it('should generate key with params', () => {
    const key = generateCacheKey('/api/test', { id: 1, name: 'test' })
    expect(key).toBe('/api/test:{"id":1,"name":"test"}')
  })

  it('should handle empty params object', () => {
    const key = generateCacheKey('/api/test', {})
    expect(key).toBe('/api/test')
  })
})
