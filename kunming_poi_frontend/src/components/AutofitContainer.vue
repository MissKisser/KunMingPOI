<!--
  自适应包装容器
  使用 CSS Transform Scale 确保内部 1920x1080 设计稿尺寸在任何屏幕下都完整且不溢出
  @author Hackerdallas
-->
<template>
  <div class="autofit-wrapper">
    <div id="autofit-content" class="autofit-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import Autofit from '../utils/autofit'

let autofitInstance: Autofit | null = null

onMounted(() => {
  autofitInstance = new Autofit({
    width: 1920,
    height: 1080,
    el: '#autofit-content'
  })
})

onBeforeUnmount(() => {
  autofitInstance?.destroy()
})
</script>

<style scoped>
.autofit-wrapper {
  position: absolute;
  inset: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: 10;
  pointer-events: none;
}

.autofit-content {
  pointer-events: none;
}
</style>
