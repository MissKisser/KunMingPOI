<!--
  SVG 流光线条组件
  @description 移植自参考项目，支持路径动画
  @author Hackerdallas
-->
<template>
  <div class="svg-line-animation" :style="{ width: `${width}px`, height: `${height}px` }">
    <svg width="100%" height="100%" :viewBox="`0 0 ${width} ${height}`" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient :id="radialGradientId" cx="50%" cy="50%" fx="100%" fy="50%" r="50%">
          <stop offset="0%" stop-color="#fff" :stop-opacity="(dir[1] as number)" />
          <stop offset="100%" stop-color="#fff" :stop-opacity="(dir[0] as number)" />
        </radialGradient>
        <mask :id="maskId">
          <circle :r="String(length)" cx="0" cy="0" :fill="`url(#${radialGradientId})`">
            <animateMotion
              :begin="`${String(begin)}s`"
              :dur="`${duration}s`"
              :path="path"
              rotate="auto"
              :keyPoints="`${String(dir[0])};${String(dir[1])}`"
              keyTimes="0;1"
              repeatCount="indefinite"
            ></animateMotion>
          </circle>
        </mask>
      </defs>
      <path
        class="path-line"
        :d="path"
        :stroke="color"
        :stroke-width="strokeWidth"
        :mask="`url(#${maskId})`"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, getCurrentInstance } from 'vue'

const props = defineProps({
  width: { type: Number, default: 135 },
  height: { type: Number, default: 150 },
  path: { type: String, default: 'M0 72.5H682L732 0.5H3082' },
  color: { type: String, default: '#0091FF' },
  duration: { type: Number, default: 3 },
  length: { type: Number, default: 100 },
  begin: { type: Number, default: 0 },
  dir: { type: Array, default: () => [0, 1] },
  strokeWidth: { type: Number, default: 4 }
})

const instance = getCurrentInstance()
const uid = instance?.uid || Math.random().toString(36).substr(2, 9)
const maskId = ref(`svgline-${uid}`)
const radialGradientId = ref(`radialGradient-${uid}`)

onMounted(() => {
  // 确保在多实例下 ID 唯一
})
</script>

<style scoped>
.svg-line-animation {
  pointer-events: none;
}
.path-line {
  mix-blend-mode: screen;
}
</style>
