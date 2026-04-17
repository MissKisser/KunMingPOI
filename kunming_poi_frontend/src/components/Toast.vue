<!--
  全局 Toast 提示组件
  支持成功、错误、警告、信息四种类型
  @author Hackerdallas
-->
<template>
  <Teleport to="body">
    <Transition name="toast-fade">
      <div v-if="visible" class="toast-container" :class="type">
        <span class="toast-icon">{{ icons[type] }}</span>
        <span class="toast-message">{{ message }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { visible, message, type, icons } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 6px;
  backdrop-filter: blur(8px);
  box-shadow: var(--glow-panel);
  font-size: 14px;
  color: var(--text-primary);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.toast-message {
  line-height: 1.4;
  max-width: 300px;
}

/* 类型样式 */
.toast-container.success .toast-icon {
  background: rgba(82, 196, 26, 0.2);
  color: #52C41A;
}

.toast-container.error .toast-icon {
  background: rgba(255, 77, 79, 0.2);
  color: #FF4D4F;
}

.toast-container.warning .toast-icon {
  background: rgba(250, 173, 20, 0.2);
  color: #FAAD14;
}

.toast-container.info .toast-icon {
  background: rgba(24, 144, 255, 0.2);
  color: #1890FF;
}

/* 动画 */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
