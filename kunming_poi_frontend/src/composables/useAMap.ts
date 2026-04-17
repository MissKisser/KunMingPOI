/**
 * 高德地图预加载模块
 * 封装 @amap/amap-jsapi-loader 服务接口
 * @author Hackerdallas
 */

import AMapLoader from '@amap/amap-jsapi-loader'
import { AMAP_KEY, AMAP_SECRET, AMAP_VERSION } from '../config/amap'

let amapLoadPromise: Promise<any> | null = null

/**
 * 高德地图 SDK 单例加载器
 */
export function useAMap(): Promise<any> {
  if (amapLoadPromise) return amapLoadPromise

  // API 请求安全密钥挂载点
  ;(window as any)._AMapSecurityConfig = {
    securityJsCode: AMAP_SECRET,
  }

  amapLoadPromise = AMapLoader.load({
    key: AMAP_KEY,
    version: AMAP_VERSION,
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.HeatMap', 'AMap.DistrictSearch'],
    Loca: { version: '2.0' },
  })

  return amapLoadPromise
}
