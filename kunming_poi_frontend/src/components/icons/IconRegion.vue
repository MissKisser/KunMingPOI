<!--
  地图区块图标 - 行政区划
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
      <path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z" />
      <path d="M8 2v16" />
      <path d="M16 6v16" />
    </g>
  </svg>
</template>
