<!--
  地图信息弹窗组件
  显示点击 POI 的详细信息
  @author Hackerdallas
-->
<template>
  <div
    v-if="visible && poi"
    class="info-window"
    :style="{ left: `${position.x}px`, top: `${position.y}px` }"
  >
    <div class="info-header">
      <span class="category-tag" :style="{ backgroundColor: categoryColor }">
        {{ poi.categoryName }}
      </span>
      <button class="close-btn" @click="close">×</button>
    </div>
    <div class="info-body">
      <h4 class="poi-name">{{ poi.name }}</h4>
      <div class="info-row">
        <span class="label">POI ID</span>
        <span class="value">{{ poi.id }}</span>
      </div>
      <div class="info-row">
        <span class="label">坐标</span>
        <span class="value">{{ poi.lng.toFixed(6) }}, {{ poi.lat.toFixed(6) }}</span>
      </div>
    </div>
    <div class="info-arrow"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CATEGORY_COLOR_MAP, DEFAULT_CATEGORY_COLOR } from '@/constants/categoryColors'

interface PoiInfo {
  id: number
  name: string
  categoryName: string
  lng: number
  lat: number
}

interface Position {
  x: number
  y: number
}

const props = defineProps<{
  visible: boolean
  poi: PoiInfo | null
  position: Position
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const categoryColor = computed(() =>
  CATEGORY_COLOR_MAP[props.poi?.categoryName || ''] || DEFAULT_CATEGORY_COLOR
)

function close() {
  emit('close')
}
</script>

<style scoped>
.info-window {
  position: fixed;
  z-index: 1000;
  min-width: 200px;
  max-width: 280px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 6px;
  backdrop-filter: blur(8px);
  box-shadow: var(--glow-panel);
  transform: translate(-50%, calc(-100% - 20px));
  animation: info-fade-in 0.2s ease-out;
}

@keyframes info-fade-in {
  from {
    opacity: 0;
    transform: translate(-50%, calc(-100% - 10px));
  }
  to {
    opacity: 1;
    transform: translate(-50%, calc(-100% - 20px));
  }
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(0, 200, 255, 0.15);
}

.category-tag {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  color: #fff;
  font-weight: 500;
}

.close-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.info-body {
  padding: 10px 12px;
}

.poi-name {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  color: rgba(255, 255, 255, 0.5);
}

.value {
  color: var(--text-secondary);
  font-family: 'MiSans-Normal', monospace;
}

.info-arrow {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid var(--panel-bg);
}

.info-arrow::before {
  content: '';
  position: absolute;
  bottom: 1px;
  left: -8px;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid var(--panel-border);
}
</style>
