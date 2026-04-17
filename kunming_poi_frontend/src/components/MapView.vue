<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useAMap } from '../composables/useAMap'
import { fetchHeatmapData, fetchPatternInstances } from '../api/index'
import type { PatternInstance, PoiDetail } from '../api/index'
import { HEATMAP_CONFIG, MAP_CONFIG, SCATTER_CONFIG, MAP_STYLE_OPTIONS, STORAGE_KEYS } from '../constants'
import { CATEGORY_COLOR_MAP, DEFAULT_CATEGORY_COLOR } from '../constants/categoryColors'
import InfoWindow from './InfoWindow.vue'

const emit = defineEmits<{
  (e: 'district-click', districtName: string): void
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const currentStyleKey = ref(localStorage.getItem(STORAGE_KEYS.MAP_STYLE) || 'blue')
const hasPatternData = ref(false)
const loading = ref(false)
const loadingText = ref('')
const panelCollapsed = ref(false)

const layerVisibility = ref({
  heatmap: true,
  scatter: true,
  convexHull: false,
  districtBoundary: true,
})

const categoryVisibility = ref<Record<string, boolean>>({})
const activeCategoriesLegend = ref<Array<{ name: string; color: string; count: number; visible: boolean }>>([])

// ─── 信息弹窗状态 ────────────────────────────────────────────────────────────
const infoWindowVisible = ref(false)
const selectedPoi = ref<{
  id: number
  name: string
  categoryName: string
  lng: number
  lat: number
} | null>(null)
const infoWindowPosition = ref({ x: 0, y: 0 })

let mapInstance: any = null
let locaInstance: any = null
let heatmapLayer: any = null
let scatterLayer: any = null
let satelliteLayer: any = null
let convexHullLayer: any = null
let districtLayers: any[] = []
let districtLabels: any[] = []

let currentInstances: PatternInstance[] = []

// ─── GeoJSON 类型定义 ─────────────────────────────────────────────────────────
interface GeoJSONFeature {
  type: string
  properties: { id: string; name: string }
  geometry: {
    type: 'Polygon' | 'MultiPolygon'
    coordinates: any // Polygon: number[][][], MultiPolygon: number[][][][]
  }
}

interface GeoJSONCollection {
  type: string
  features: GeoJSONFeature[]
}

// 区县简称映射（用于地图标注显示）
const DISTRICT_SHORT_NAME: Record<string, string> = {
  '石林彝族自治县': '石林县',
  '寻甸回族彝族自治县': '寻甸县',
  '禄劝彝族苗族自治县': '禄劝县',
}

onMounted(async () => {
  console.log('[MapView] 开始初始化地图')
  try {
    const AMap = await useAMap()
    console.log('[Amap] SDK 加载完成')

    satelliteLayer = new AMap.TileLayer.Satellite()

    mapInstance = new AMap.Map(mapContainer.value, {
      viewMode: '3D',
      zoom: MAP_CONFIG.INITIAL_ZOOM,
      center: MAP_CONFIG.CENTER,
      mapStyle: 'amap://styles/normal',
      pitch: 0,
      skyColor: '#000000',
      showLabel: true,
      showBuildingBlock: true,
      features: ['bg', 'building'],
      pitchEnable: true,
      rotateEnable: true,
      keyboardEnable: false,
      dragEnable: true,
      zoomEnable: true,
    })

    // 初始化时默认添加卫星底图
    mapInstance.add(satelliteLayer)
    console.log('[Amap] 初始化完成，默认使用卫星底图')

    mapInstance.on('complete', () => {
      console.log('[Amap] 地图实例创建完成，等待看板展开')

      // 停顿等待看板展开
      setTimeout(() => {
        // 根据缓存设置切换底图
        const savedStyle = localStorage.getItem(STORAGE_KEYS.MAP_STYLE)
        console.log('[Amap] 检查底图缓存设置:', savedStyle || '无缓存')

        if (savedStyle) {
          // 有缓存设置，切换到用户选择的底图
          const selected = MAP_STYLE_OPTIONS.find(o => o.key === savedStyle)
          if (selected) {
            if (selected.key === 'satellite') {
              console.log('[Amap] 使用缓存的卫星底图')
            } else {
              mapInstance.remove(satelliteLayer)
              mapInstance.setMapStyle(selected.style)
              console.log('[Amap] 切换到缓存底图:', selected.label)
            }
          }
        } else {
          mapInstance.remove(satelliteLayer)
          mapInstance.setMapStyle('amap://styles/blue')
          console.log('[Amap] 无缓存，切换到默认深蓝科技底图')
        }

        console.log('[Amap] 开始飞入动画')
        mapInstance.setZoomAndCenter(MAP_CONFIG.TARGET_ZOOM, MAP_CONFIG.CENTER, false, MAP_CONFIG.FLY_DURATION)

        setTimeout(() => {
          mapInstance.setPitch(MAP_CONFIG.TARGET_PITCH, false, MAP_CONFIG.PITCH_DURATION)
        }, MAP_CONFIG.FLY_DURATION)
      }, MAP_CONFIG.WAIT_FOR_HEADER)
    })

    await initHeatmapLayer(AMap)

    if (!(window as any).Loca) {
      throw new Error('Loca 可视化库未加载')
    }
    locaInstance = new (window as any).Loca.Container({ map: mapInstance })
    console.log('[Loca] 容器创建成功')

    initScatterLayer()

    // 初始化区域边界（基于本地 GeoJSON 数据）
    await initDistrictBoundaries(AMap)

    locaInstance.animate.start()
    console.log('[MapView] 所有图层初始化完成')

  } catch (err) {
    console.error('[MapView] 初始化异常:', err)
  }
})

onBeforeUnmount(() => {
  if (locaInstance) {
    locaInstance.destroy()
  }
  if (mapInstance) {
    mapInstance.destroy()
  }
})

// ─── 区域边界模块 ─────────────────────────────────────────────────────────────
// 数据源：昆明市行政区划 Shapefile（530100）转换的 GeoJSON 文件
// 覆盖全部14个区县，边界精度源自国家测绘数据

/**
 * 加载本地 GeoJSON 并渲染所有区县边界
 */
async function initDistrictBoundaries(AMap: any) {
  try {
    console.log('[District] 开始加载区域边界（GeoJSON 数据源）')

    const response = await fetch('/kunming_districts.geojson')
    if (!response.ok) {
      throw new Error(`GeoJSON 加载失败: ${response.status}`)
    }

    const geojson: GeoJSONCollection = await response.json()
    console.log('[District] GeoJSON 解析完成，共', geojson.features.length, '个区县')

    geojson.features.forEach(feature => {
      createDistrictBoundary(AMap, feature)
    })

    console.log('[District] 区域边界渲染完成，共', districtLayers.length, '个多边形')

  } catch (err) {
    console.error('[District] 初始化区域边界异常:', err)
  }
}

/**
 * 创建区县边界多边形
 * Polygon:      coordinates = [[外环], [内环...]]  → 1个 AMap.Polygon
 * MultiPolygon: coordinates = [[[外环], [内环...]], ...] → 每个子多边形独立创建
 */
function createDistrictBoundary(AMap: any, feature: GeoJSONFeature) {
  const { type, coordinates } = feature.geometry
  const { name } = feature.properties

  if (!coordinates || coordinates.length === 0) return

  // 统一为 polygons 数组：[[[外环], [内环...]], ...]
  const polygons: number[][][][] = type === 'MultiPolygon' ? coordinates : [coordinates]

  // 跟踪面积最大的多边形，标注放在最大块上
  let maxArea = 0
  let labelCenter: [number, number] | null = null

  polygons.forEach((polyCoords: number[][][]) => {
    const polygon = new AMap.Polygon({
      path: polyCoords,
      strokeColor: '#3EE5FF',
      strokeWeight: 2,
      strokeOpacity: 0.9,
      fillColor: '#3EE5FF',
      fillOpacity: 0.12,
      zIndex: 50,
      extData: { name },
    })

    // 同一区县的多个多边形联动高亮
    polygon.on('mouseover', () => {
      districtLayers.forEach((layer: any) => {
        if (layer.getExtData()?.name === name) {
          layer.setOptions({ fillOpacity: 0.35, strokeWeight: 4, strokeColor: '#00FFFF' })
        }
      })
    })

    polygon.on('mouseout', () => {
      districtLayers.forEach((layer: any) => {
        if (layer.getExtData()?.name === name) {
          layer.setOptions({ fillOpacity: 0.12, strokeWeight: 2, strokeColor: '#3EE5FF' })
        }
      })
    })

    polygon.on('click', () => {
      emit('district-click', name)
    })

    mapInstance.add(polygon)
    districtLayers.push(polygon)

    // 选最大外环放标注
    const outerRing = polyCoords[0]
    if (outerRing) {
      const area = Math.abs(ringArea(outerRing))
      if (area > maxArea) {
        maxArea = area
        labelCenter = getPolygonCenter(outerRing)
      }
    }
  })

  // 标注文字：在面积最大的多边形中心显示一次
  if (labelCenter) {
    const displayName = DISTRICT_SHORT_NAME[name] || name
    const marker = new AMap.Text({
      text: displayName,
      position: labelCenter,
      style: {
        'background-color': 'transparent',
        'border': 'none',
        'color': '#3EE5FF',
        'font-size': '12px',
        'font-weight': '500',
        'text-shadow': '0 0 8px rgba(62, 229, 255, 0.8)',
      },
      zIndex: 15,
    })
    mapInstance.add(marker)
    districtLabels.push(marker)
  }

  console.log('[District] 渲染边界:', name, `(${type}, ${polygons.length}块)`)
}

/**
 * 计算多边形环的几何质心
 */
function getPolygonCenter(ring: number[][]): [number, number] | null {
  if (!ring || ring.length === 0) return null

  let sumLng = 0
  let sumLat = 0
  ring.forEach(p => {
    sumLng += p[0] ?? 0
    sumLat += p[1] ?? 0
  })

  return [sumLng / ring.length, sumLat / ring.length]
}

/**
 * Shoelace 公式计算环的有符号面积
 */
function ringArea(ring: number[][]): number {
  let area = 0
  const n = ring.length
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n
    const pi = ring[i]!
    const pj = ring[j]!
    area += pi[0] * pj[1]
    area -= pj[0] * pi[1]
  }
  return area / 2
}

/**
 * 高亮指定区域
 */
function highlightDistrict(districtName: string) {
  districtLayers.forEach(layer => {
    const name = layer.getExtData()?.name
    if (name === districtName) {
      layer.setOptions({
        fillOpacity: 0.45,
        strokeWeight: 4,
        strokeColor: '#00FFFF',
      })
    } else {
      layer.setOptions({
        fillOpacity: 0.12,
        strokeWeight: 2,
        strokeColor: '#3EE5FF',
      })
    }
  })
}

/**
 * AMap.HeatMap 热力图初始化
 * 采用渐进式加载策略：首屏快速加载核心数据，后台加载完整数据
 */
async function initHeatmapLayer(AMap: any) {
  try {
    console.log('[Heatmap] 开始加载热力图数据（渐进式加载）')
    loading.value = true
    loadingText.value = '加载热力图数据...'

    // 第一阶段：快速加载核心数据（10000 点）
    console.log('[Heatmap] 第一阶段：加载核心数据')
    const coreData = await fetchHeatmapData(HEATMAP_CONFIG.INITIAL_LOAD_LIMIT)

    if (!Array.isArray(coreData) || coreData.length === 0) {
      throw new Error('后端返回空数据或格式错误')
    }

    const firstPoint = coreData[0]
    if (!firstPoint || typeof firstPoint.lng !== 'number' || typeof firstPoint.lat !== 'number') {
      throw new Error('数据格式不正确，缺少 lng 或 lat 字段')
    }

    // plugin 回调保证 AMap.HeatMap 构造函数在插件就绪后执行
    await new Promise<void>((resolve, reject) => {
      mapInstance.plugin(['AMap.HeatMap'], () => {
        try {
          heatmapLayer = new AMap.HeatMap(mapInstance, {
            radius: HEATMAP_CONFIG.RADIUS,
            opacity: HEATMAP_CONFIG.OPACITY,
            gradient: HEATMAP_CONFIG.GRADIENT,
            zooms: HEATMAP_CONFIG.ZOOMS,
            visible: true,
            zIndex: HEATMAP_CONFIG.Z_INDEX,
          })

          // 渲染核心数据
          const corePoints = coreData.map(({ lng, lat }: { lng: number; lat: number }) => ({
            lng,
            lat,
            count: 1,
          }))
          heatmapLayer.setDataSet({ data: corePoints, max: HEATMAP_CONFIG.MAX_COUNT })

          console.log('[Heatmap] 核心数据渲染完成，数据点数:', corePoints.length)
          resolve()
        } catch (e) {
          reject(e)
        }
      })
    })

    loading.value = false

    // 第二阶段：后台加载完整数据
    console.log('[Heatmap] 第二阶段：后台加载完整数据')
    setTimeout(async () => {
      try {
        const fullData = await fetchHeatmapData(HEATMAP_CONFIG.DATA_LIMIT)
        const fullPoints = fullData.map(({ lng, lat }: { lng: number; lat: number }) => ({
          lng,
          lat,
          count: 1,
        }))
        heatmapLayer.setDataSet({ data: fullPoints, max: HEATMAP_CONFIG.MAX_COUNT })
        console.log('[Heatmap] 完整数据渲染完成，数据点数:', fullPoints.length)
      } catch (err) {
        console.warn('[Heatmap] 后台加载完整数据失败，使用核心数据:', err)
      }
    }, 100)

  } catch (err) {
    console.error('[Heatmap] 加载失败:', err)
    loading.value = false
  }
}

function initScatterLayer() {
  scatterLayer = new (window as any).Loca.ScatterLayer({
    zIndex: SCATTER_CONFIG.Z_INDEX,
    opacity: SCATTER_CONFIG.OPACITY,
    visible: true,
    zooms: SCATTER_CONFIG.ZOOMS,
  })

  const emptyGeoData = { type: 'FeatureCollection', features: [] }
  scatterLayer.setSource(new (window as any).Loca.GeoJSONSource({ data: emptyGeoData }))

  scatterLayer.setStyle({
    unit: 'px',
    size: SCATTER_CONFIG.SIZE,
    borderWidth: SCATTER_CONFIG.BORDER_WIDTH,
    borderColor: SCATTER_CONFIG.BORDER_COLOR,
    color: (_: number, feature: any) => {
      const category = feature.properties.category
      return CATEGORY_COLOR_MAP[category] || DEFAULT_CATEGORY_COLOR
    },
  })

  // 添加点击事件
  scatterLayer.on('click', (event: any) => {
    const feature = event.feature
    if (feature && feature.properties) {
      const coords = feature.geometry.coordinates
      showInfoWindow({
        id: feature.properties.poi_id,
        name: feature.properties.name,
        categoryName: feature.properties.category,
        lng: coords[0],
        lat: coords[1],
      })
    }
  })

  locaInstance.add(scatterLayer)
  console.log('[Scatter] 散点图层已添加到容器')
  console.log('[Scatter] 散点图层初始化完成')
}

function onStyleChange() {
  if (!mapInstance) return

  const selected = MAP_STYLE_OPTIONS.find(o => o.key === currentStyleKey.value)
  if (!selected) return

  // 保存用户选择到 localStorage
  localStorage.setItem(STORAGE_KEYS.MAP_STYLE, currentStyleKey.value)

  if (selected.key === 'satellite') {
    mapInstance.setMapStyle('amap://styles/normal')
    mapInstance.add(satelliteLayer)
  } else {
    mapInstance.remove(satelliteLayer)
    mapInstance.setMapStyle(selected.style)
  }
}

async function renderPattern(patternId: number) {
  try {
    console.log('[Pattern] 开始加载模式数据, patternId:', patternId)
    loading.value = true
    loadingText.value = '加载模式数据...'

    const data = await fetchPatternInstances(patternId)
    currentInstances = data

    if (!currentInstances.length) {
      console.warn('[Pattern] 该模式无实例数据')
      loading.value = false
      return
    }

    console.log('[Pattern] 模式数据加载完成，实例数:', currentInstances.length)

    hasPatternData.value = true

    renderScatterLayer(currentInstances)
    updateLegend(currentInstances)

    loading.value = false
    console.log('[Pattern] 模式渲染完成')

  } catch (err) {
    console.error('[Pattern] 渲染失败:', err)
    loading.value = false
  }
}

function renderScatterLayer(instances: PatternInstance[]) {
  if (!scatterLayer) return

  console.log('[Scatter] 开始渲染散点图')

  const allPois: PoiDetail[] = []
  instances.forEach(inst => {
    allPois.push(...inst.pois)
  })

  console.log('[Scatter] 总POI数量:', allPois.length)

  const geoData = {
    type: 'FeatureCollection',
    features: allPois
      .filter(poi => {
        const visible = categoryVisibility.value[poi.category_name]
        return visible === undefined || visible
      })
      .map(poi => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [poi.lng, poi.lat] },
        properties: {
          category: poi.category_name,
          name: poi.poi_name,
          poi_id: poi.poi_id,
        },
      })),
  }

  console.log('[Scatter] 渲染POI数量:', geoData.features.length)
  scatterLayer.setSource(new (window as any).Loca.GeoJSONSource({ data: geoData }))
}

function updateLegend(instances: PatternInstance[]) {
  const categoryCount: Record<string, number> = {}

  instances.forEach(inst => {
    inst.pois.forEach(poi => {
      categoryCount[poi.category_name] = (categoryCount[poi.category_name] || 0) + 1
    })
  })

  activeCategoriesLegend.value = Object.entries(categoryCount).map(([name, count]) => ({
    name,
    color: CATEGORY_COLOR_MAP[name] || DEFAULT_CATEGORY_COLOR,
    count,
    visible: categoryVisibility.value[name] !== false,
  }))

  Object.keys(categoryCount).forEach(name => {
    if (categoryVisibility.value[name] === undefined) {
      categoryVisibility.value[name] = true
    }
  })

  console.log('[Legend] 图例更新完成，类别数:', activeCategoriesLegend.value.length)
}

function toggleHeatmap(visible: boolean) {
  if (!heatmapLayer) return
  visible ? heatmapLayer.show() : heatmapLayer.hide()
}

function toggleScatter(visible: boolean) {
  if (scatterLayer) {
    scatterLayer.visible = visible
  }
}

function toggleConvexHull(visible: boolean) {
  if (convexHullLayer) {
    convexHullLayer.visible = visible
  }
}

function toggleDistrictBoundary(visible: boolean) {
  districtLayers.forEach(layer => {
    visible ? layer.show() : layer.hide()
  })
  districtLabels.forEach(label => {
    visible ? label.show() : label.hide()
  })
}

function toggleCategory(categoryName: string) {
  categoryVisibility.value[categoryName] = !categoryVisibility.value[categoryName]

  const item = activeCategoriesLegend.value.find(c => c.name === categoryName)
  if (item) {
    item.visible = categoryVisibility.value[categoryName]
  }

  if (currentInstances.length) {
    renderScatterLayer(currentInstances)
  }
}

// ─── 信息弹窗控制 ────────────────────────────────────────────────────────────

function showInfoWindow(poi: { id: number; name: string; categoryName: string; lng: number; lat: number }) {
  selectedPoi.value = poi
  infoWindowVisible.value = true

  // 计算弹窗位置（屏幕坐标）
  if (mapInstance) {
    const pixel = mapInstance.lngLatToContainer([poi.lng, poi.lat])
    infoWindowPosition.value = { x: pixel.x, y: pixel.y }
  }
}

function hideInfoWindow() {
  infoWindowVisible.value = false
  selectedPoi.value = null
}

defineExpose({
  renderPattern,
  toggleHeatmap,
  toggleScatter,
  toggleConvexHull,
  toggleDistrictBoundary,
  highlightDistrict,
})
</script>

<template>
  <div class="map-container">
    <div ref="mapContainer" class="map-inner-container" style="width: 100%; height: 100%;" />

    <div class="map-style-selector">
      <span class="selector-label">底图样式</span>
      <div class="selector-wrapper">
        <select v-model="currentStyleKey" @change="onStyleChange" class="style-select">
          <option v-for="opt in MAP_STYLE_OPTIONS" :key="opt.key" :value="opt.key">
            {{ opt.label }}
          </option>
        </select>
        <span class="selector-arrow">▾</span>
      </div>
    </div>

    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <div class="loading-text">{{ loadingText }}</div>
    </div>

    <div class="layer-control-panel" v-if="hasPatternData">
      <div class="panel-header">
        <span class="panel-title">图层控制</span>
        <button class="panel-toggle" @click="panelCollapsed = !panelCollapsed">
          {{ panelCollapsed ? '展开' : '收起' }}
        </button>
      </div>

      <div class="panel-content" :class="{ collapsed: panelCollapsed }">
        <div class="control-item">
          <label class="control-label">
            <input type="checkbox" v-model="layerVisibility.districtBoundary" @change="toggleDistrictBoundary(layerVisibility.districtBoundary)">
            <span>区域边界</span>
          </label>
        </div>

        <div class="control-item">
          <label class="control-label">
            <input type="checkbox" v-model="layerVisibility.heatmap" @change="toggleHeatmap(layerVisibility.heatmap)">
            <span>热力图底图</span>
          </label>
        </div>

        <div class="control-item">
          <label class="control-label">
            <input type="checkbox" v-model="layerVisibility.scatter" @change="toggleScatter(layerVisibility.scatter)">
            <span>类别散点图</span>
          </label>
        </div>

        <div class="category-legend" v-if="layerVisibility.scatter && activeCategoriesLegend.length > 0">
          <div class="legend-header">
            <span class="legend-title">类别图例</span>
            <span class="legend-count">({{ activeCategoriesLegend.length }})</span>
          </div>
          <div class="legend-list">
            <div
              v-for="cat in activeCategoriesLegend"
              :key="cat.name"
              class="legend-item"
              @click="toggleCategory(cat.name)"
              :class="{ disabled: !cat.visible }"
            >
              <span class="legend-color" :style="{ backgroundColor: cat.color }"></span>
              <span class="legend-name">{{ cat.name }}</span>
              <span class="legend-count">({{ cat.count }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 信息弹窗 -->
    <InfoWindow
      :visible="infoWindowVisible"
      :poi="selectedPoi"
      :position="infoWindowPosition"
      @close="hideInfoWindow"
    />
  </div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-style-selector {
  position: absolute;
  bottom: 16px;
  right: 12px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 18, 40, 0.82);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 4px;
  padding: 5px 10px;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 10px rgba(0, 200, 255, 0.15);
}

.selector-label {
  font-size: 12px;
  color: rgba(0, 200, 255, 0.75);
  white-space: nowrap;
  letter-spacing: 0.05em;
}

.selector-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.style-select {
  appearance: none;
  background: transparent;
  border: none;
  color: #e0f4ff;
  font-size: 12px;
  padding: 2px 20px 2px 4px;
  cursor: pointer;
  outline: none;
  letter-spacing: 0.04em;
}

.style-select option {
  background: #011428;
  color: #e0f4ff;
}

.selector-arrow {
  position: absolute;
  right: 0;
  font-size: 10px;
  color: rgba(0, 200, 255, 0.7);
  pointer-events: none;
}

.loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  background: rgba(0, 18, 40, 0.9);
  padding: 24px 32px;
  border-radius: 8px;
  border: 1px solid rgba(0, 200, 255, 0.3);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 200, 255, 0.1);
  border-top-color: #00c8ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 14px;
  color: #e0f4ff;
  letter-spacing: 1px;
}

.layer-control-panel {
  position: absolute;
  bottom: 60px;
  right: 12px;
  z-index: 100;
  background: rgba(0, 18, 40, 0.9);
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 6px;
  backdrop-filter: blur(8px);
  box-shadow: 0 0 15px rgba(0, 200, 255, 0.2);
  min-width: 180px;
  max-width: 220px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(0, 200, 255, 0.2);
}

.panel-title {
  font-size: 13px;
  color: #00c8ff;
  font-weight: 600;
}

.panel-toggle {
  font-size: 11px;
  color: rgba(0, 200, 255, 0.7);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 3px;
  transition: all 0.2s;
}

.panel-toggle:hover {
  background: rgba(0, 200, 255, 0.1);
  color: #00c8ff;
}

.panel-content {
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
  transition: max-height 0.3s ease, padding 0.3s ease;
}

.panel-content.collapsed {
  max-height: 0;
  padding: 0 12px;
  overflow: hidden;
}

.panel-title {
  font-size: 13px;
  color: #00c8ff;
  font-weight: 600;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 200, 255, 0.2);
}

.control-item {
  margin-bottom: 8px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #e0f4ff;
  cursor: pointer;
  user-select: none;
}

.control-label input[type="checkbox"] {
  cursor: pointer;
  accent-color: #00c8ff;
}

.category-legend {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 200, 255, 0.2);
}

.legend-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.legend-title {
  font-size: 12px;
  color: #00c8ff;
  font-weight: 600;
}

.legend-count {
  font-size: 10px;
  color: rgba(0, 200, 255, 0.6);
}

.legend-list {
  max-height: 200px;
  overflow-y: auto;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #e0f4ff;
  margin-bottom: 6px;
  cursor: pointer;
  padding: 3px 4px;
  border-radius: 3px;
  transition: all 0.2s;
}

.legend-item:hover {
  background: rgba(0, 200, 255, 0.1);
}

.legend-item.disabled {
  opacity: 0.4;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.legend-count {
  font-size: 10px;
  color: rgba(0, 200, 255, 0.6);
}
</style>
