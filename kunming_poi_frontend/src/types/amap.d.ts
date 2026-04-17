/**
 * 高德地图 JS API 类型声明
 * 为 AMap 和 Loca 提供基本的 TypeScript 类型支持
 * @author Hackerdallas
 */

declare namespace AMap {
  // ─── 地图核心类 ────────────────────────────────────────────────────────────

  class Map {
    constructor(container: HTMLElement | string, options: MapOptions)

    // 视图控制
    setZoomAndCenter(
      zoom: number,
      center: [number, number],
      immediately?: boolean,
      duration?: number
    ): void
    setZoom(zoom: number, immediately?: boolean, duration?: number): void
    setCenter(center: [number, number]): void
    setPitch(pitch: number, immediately?: boolean, duration?: number): void
    setMapStyle(style: string): void
    getZoom(): number
    getCenter(): LngLat
    getBounds(): Bounds
    getPitch(): number

    // 图层管理
    add(layer: Layer): void
    remove(layer: Layer): void

    // 事件
    on(event: string, handler: Function): void
    off(event: string, handler: Function): void

    // 插件
    plugin(plugins: string[], callback: Function): void

    // 坐标转换
    lngLatToContainer(lnglat: [number, number]): Pixel
    containerToLngLat(pixel: Pixel): LngLat

    // 销毁
    destroy(): void
  }

  interface MapOptions {
    viewMode?: '2D' | '3D'
    zoom?: number
    center?: [number, number]
    mapStyle?: string
    pitch?: number
    skyColor?: string
    showLabel?: boolean
    showBuildingBlock?: boolean
    features?: string[]
    pitchEnable?: boolean
    rotateEnable?: boolean
    keyboardEnable?: boolean
    dragEnable?: boolean
    zoomEnable?: boolean
  }

  // ─── 图层类 ────────────────────────────────────────────────────────────────

  class Layer {
    show(): void
    hide(): void
  }

  namespace TileLayer {
    class Satellite extends Layer {
      constructor(options?: TileLayerOptions)
    }
  }

  interface TileLayerOptions {
    zIndex?: number
    opacity?: number
    visible?: boolean
  }

  // ─── 热力图 ────────────────────────────────────────────────────────────────

  class HeatMap {
    constructor(map: Map, options: HeatMapOptions)
    setDataSet(data: { data: HeatMapPoint[]; max: number }): void
    show(): void
    hide(): void
  }

  interface HeatMapOptions {
    radius: number
    opacity: [number, number]
    gradient: Record<number, string>
    zooms: [number, number]
    visible: boolean
    zIndex: number
  }

  interface HeatMapPoint {
    lng: number
    lat: number
    count: number
  }

  // ─── 坐标与边界 ────────────────────────────────────────────────────────────

  interface LngLat {
    getLng(): number
    getLat(): number
  }

  interface Bounds {
    getSouthWest(): LngLat
    getNorthEast(): LngLat
  }

  interface Pixel {
    x: number
    y: number
  }
}

// ─── Loca 可视化库 ────────────────────────────────────────────────────────────

declare namespace Loca {
  class Container {
    constructor(options: { map: AMap.Map })
    add(layer: Layer): void
    animate: { start(): void }
    destroy(): void
  }

  class Layer {
    setSource(source: GeoJSONSource): void
    setStyle(style: LayerStyle): void
    visible: boolean
    on(event: string, handler: Function): void
    off(event: string, handler: Function): void
  }

  class ScatterLayer extends Layer {
    constructor(options: LayerOptions)
  }

  class HeatMapLayer extends Layer {
    constructor(options: LayerOptions)
  }

  class GeoJSONSource {
    constructor(options: { data: GeoJSON.FeatureCollection })
  }

  interface LayerOptions {
    zIndex?: number
    opacity?: number
    visible?: boolean
    zooms?: [number, number]
  }

  interface LayerStyle {
    unit?: string
    size?: [number, number]
    borderWidth?: number
    borderColor?: string
    color?: string | ((value: number, feature: GeoJSON.Feature) => string)
    radius?: number | ((value: number, feature: GeoJSON.Feature) => number)
  }
}

// ─── 全局变量声明 ─────────────────────────────────────────────────────────────

declare const AMap: {
  Map: typeof AMap.Map
  TileLayer: typeof AMap.TileLayer & {
    Satellite: typeof AMap.TileLayer.Satellite
  }
  HeatMap: typeof AMap.HeatMap
}

declare const Loca: {
  Container: typeof Loca.Container
  ScatterLayer: typeof Loca.ScatterLayer
  HeatMapLayer: typeof Loca.HeatMapLayer
  GeoJSONSource: typeof Loca.GeoJSONSource
}

// ─── Window 扩展 ──────────────────────────────────────────────────────────────

interface Window {
  _AMapSecurityConfig?: {
    securityJsCode: string
  }
  Loca?: typeof Loca
}
