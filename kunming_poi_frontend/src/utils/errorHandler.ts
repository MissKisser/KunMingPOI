/**
 * 全局错误处理
 * @author Hackerdallas
 */

import { useToast } from '@/composables/useToast'

const toast = useToast()

export function setupGlobalErrorHandler() {
  window.addEventListener('error', (event) => {
    console.error('[Global Error]', event.error)
    toast.error('发生未知错误，请刷新页面重试')
  })

  window.addEventListener('unhandledrejection', (event) => {
    console.error('[Unhandled Promise Rejection]', event.reason)

    const reason = event.reason
    if (reason?.response) {
      const status = reason.response.status
      if (status === 401) {
        toast.error('登录已过期，请重新登录')
      } else if (status === 403) {
        toast.error('无权限访问该资源')
      } else if (status >= 500) {
        toast.error('服务器错误，请稍后重试')
      } else {
        toast.error('请求失败，请检查网络')
      }
    } else if (reason?.message) {
      toast.error(reason.message)
    } else {
      toast.error('异步操作失败')
    }
  })
}

export function handleApiError(error: unknown, fallbackMessage = '操作失败'): string {
  if (error instanceof Error) {
    return error.message || fallbackMessage
  }
  if (typeof error === 'string') {
    return error
  }
  if (error && typeof error === 'object' && 'detail' in error) {
    return String((error as { detail: string }).detail)
  }
  return fallbackMessage
}
