/**
 * 全局 Toast 提示 Composable
 * 提供统一的消息提示能力
 * @author Hackerdallas
 */

import { ref, readonly } from 'vue'

/** Toast 类型 */
export type ToastType = 'success' | 'error' | 'warning' | 'info'

/** Toast 配置 */
interface ToastOptions {
  /** 消息内容 */
  message: string
  /** Toast 类型 */
  type?: ToastType
  /** 显示时长（毫秒），默认 3000 */
  duration?: number
}

// 全局状态
const visible = ref(false)
const message = ref('')
const type = ref<ToastType>('info')
let hideTimer: ReturnType<typeof setTimeout> | null = null

// 类型对应的图标
const TOAST_ICONS: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

// 类型对应的颜色
const TOAST_COLORS: Record<ToastType, string> = {
  success: '#52C41A',
  error: '#FF4D4F',
  warning: '#FAAD14',
  info: '#1890FF',
}

/**
 * 显示 Toast
 */
function show(options: ToastOptions): void
function show(message: string, type?: ToastType): void
function show(optionsOrMessage: ToastOptions | string, toastType?: ToastType): void {
  // 清除之前的定时器
  if (hideTimer) {
    clearTimeout(hideTimer)
  }

  // 解析参数
  const options: ToastOptions =
    typeof optionsOrMessage === 'string'
      ? { message: optionsOrMessage, type: toastType }
      : optionsOrMessage

  // 设置状态
  message.value = options.message
  type.value = options.type || 'info'
  visible.value = true

  // 自动隐藏
  const duration = options.duration ?? 3000
  hideTimer = setTimeout(() => {
    hide()
  }, duration)
}

/**
 * 隐藏 Toast
 */
function hide(): void {
  visible.value = false
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

/**
 * 快捷方法
 */
const success = (msg: string) => show(msg, 'success')
const error = (msg: string) => show(msg, 'error')
const warning = (msg: string) => show(msg, 'warning')
const info = (msg: string) => show(msg, 'info')

/**
 * Toast Composable
 *
 * @example
 * ```typescript
 * import { useToast } from '@/composables/useToast'
 *
 * const toast = useToast()
 *
 * // 显示错误提示
 * toast.error('操作失败')
 *
 * // 显示成功提示
 * toast.success('保存成功')
 *
 * // 自定义配置
 * toast.show({ message: '处理中...', type: 'info', duration: 5000 })
 * ```
 */
export function useToast() {
  return {
    visible: readonly(visible),
    message: readonly(message),
    type: readonly(type),
    icons: TOAST_ICONS,
    colors: TOAST_COLORS,
    show,
    hide,
    success,
    error,
    warning,
    info,
  }
}
