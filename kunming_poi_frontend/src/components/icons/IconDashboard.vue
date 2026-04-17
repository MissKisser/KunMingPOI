<!--
  SVG 图标组件
  统一的线性图标风格，适配科技蓝主题
  @author Hackerdallas
-->
<script setup lang="ts">
defineProps<{
  size?: number
  color?: string
}>()
</script>

<template>
  <svg
    :width="size || 20"
    :height="size || 20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g :stroke="color || 'currentColor'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <!-- 仪表盘图标 - 态势感知 -->
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </g>
  </svg>
</template>
