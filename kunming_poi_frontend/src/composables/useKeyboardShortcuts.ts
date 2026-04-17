/**
 * 键盘快捷键管理
 * @author Hackerdallas
 */

import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

interface ShortcutConfig {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  description: string
  action: () => void
}

const shortcuts: ShortcutConfig[] = [
  { key: '1', description: '跳转到态势感知', action: () => {} },
  { key: '2', description: '跳转到模式分析', action: () => {} },
  { key: '3', description: '跳转到区域分析', action: () => {} },
  { key: '4', description: '跳转到数据总览', action: () => {} },
  { key: 'r', ctrl: true, description: '刷新数据', action: () => window.location.reload() },
  { key: '?', shift: true, description: '显示快捷键帮助', action: () => {} },
]

export function useKeyboardShortcuts() {
  const router = useRouter()

  const routeActions: Record<string, string> = {
    '1': '/',
    '2': '/patterns',
    '3': '/districts',
    '4': '/overview',
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
      return
    }

    for (const shortcut of shortcuts) {
      const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()
      const ctrlMatch = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey
      const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey
      const altMatch = shortcut.alt ? event.altKey : !event.altKey

      if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
        event.preventDefault()

        const route = routeActions[shortcut.key]
        if (route) {
          router.push(route)
        } else {
          shortcut.action()
        }
        break
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })

  return { shortcuts }
}

export function getShortcutsList(): ShortcutConfig[] {
  return shortcuts
}
