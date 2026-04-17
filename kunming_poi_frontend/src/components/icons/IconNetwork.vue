<!--
  模式分析图标 - 链接网络
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
      <circle cx="6" cy="6" r="3" />
      <circle cx="18" cy="6" r="3" />
      <circle cx="6" cy="18" r="3" />
      <circle cx="18" cy="18" r="3" />
      <path d="M9 6h6" />
      <path d="M6 9v6" />
      <path d="M18 9v6" />
      <path d="M9 18h6" />
    </g>
  </svg>
</template>
