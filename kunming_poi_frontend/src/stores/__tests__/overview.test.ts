import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOverviewStore } from '../modules/overview'

describe('useOverviewStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default values', () => {
    const store = useOverviewStore()

    expect(store.poiTotal).toBe(0)
    expect(store.patternTotal).toBe(0)
    expect(store.instanceTotal).toBe(0)
    expect(store.categoryStats).toEqual([])
    expect(store.districtSummary).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('should compute overviewStats correctly', () => {
    const store = useOverviewStore()

    store.poiTotal = 1000
    store.patternTotal = 100
    store.instanceTotal = 500

    expect(store.overviewStats).toEqual([
      { label: 'POI 总量', value: '1,000' },
      { label: '挖掘模式数', value: '100' },
      { label: '模式实例数', value: '500' },
    ])
  })

  it('should compute pieData correctly', () => {
    const store = useOverviewStore()

    store.categoryStats = [
      { category_name: '餐饮', category_code: 'C1', description: '', poi_count: 100 },
      { category_name: '购物', category_code: 'C2', description: '', poi_count: 200 },
    ]

    expect(store.pieData).toEqual([
      { name: '餐饮', value: 100 },
      { name: '购物', value: 200 },
    ])
  })

  it('should compute categoryCount correctly', () => {
    const store = useOverviewStore()

    expect(store.categoryCount).toBe(0)

    store.categoryStats = [
      { category_name: 'A', category_code: 'A1', description: '', poi_count: 1 },
      { category_name: 'B', category_code: 'B1', description: '', poi_count: 2 },
      { category_name: 'C', category_code: 'C1', description: '', poi_count: 3 },
    ]

    expect(store.categoryCount).toBe(3)
  })

  it('should compute districtCount correctly', () => {
    const store = useOverviewStore()

    expect(store.districtCount).toBe(0)

    store.districtSummary = [
      { district: '五华区', poi_count: 100, pattern_count: 10 },
      { district: '盘龙区', poi_count: 200, pattern_count: 20 },
    ]

    expect(store.districtCount).toBe(2)
  })

  it('should reset state', () => {
    const store = useOverviewStore()

    store.poiTotal = 1000
    store.patternTotal = 100
    store.loading = true
    store.error = 'test error'

    store.reset()

    expect(store.poiTotal).toBe(0)
    expect(store.patternTotal).toBe(0)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })
})
