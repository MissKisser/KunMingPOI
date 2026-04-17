/**
 * POI 类别颜色映射
 * 统一管理各类别的显示颜色
 * @author Hackerdallas
 */

export const CATEGORY_COLOR_MAP: Record<string, string> = {
  '购物消费': '#FF6B6B',
  '科教文化': '#4ECDC4',
  '医疗保健': '#45B7D1',
  '汽车相关': '#FFA07A',
  '生活服务': '#98D8C8',
  '交通设施': '#F7DC6F',
  '餐饮美食': '#BB8FCE',
  '休闲娱乐': '#F8B739',
  '运动健身': '#52C41A',
}

/** 默认类别颜色 */
export const DEFAULT_CATEGORY_COLOR = '#00c8ff'

/**
 * 获取类别颜色
 * @param categoryName 类别名称
 * @returns 颜色值
 */
export function getCategoryColor(categoryName: string): string {
  return CATEGORY_COLOR_MAP[categoryName] || DEFAULT_CATEGORY_COLOR
}
