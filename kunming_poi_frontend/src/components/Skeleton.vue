<!--
  骨架屏组件
  提供加载时的占位效果，提升用户体验
  @author Hackerdallas
-->
<template>
  <div class="skeleton" :class="variant">
    <!-- 统计卡片骨架 -->
    <template v-if="variant === 'stats'">
      <div class="skeleton-stats">
        <div v-for="i in 3" :key="i" class="skeleton-stat-item">
          <div class="skeleton-circle"></div>
          <div class="skeleton-lines">
            <div class="skeleton-line short"></div>
            <div class="skeleton-line title"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 图表骨架 -->
    <template v-else-if="variant === 'chart'">
      <div class="skeleton-chart">
        <div v-for="i in rows" :key="i" class="skeleton-bar" :style="{ width: `${30 + Math.random() * 60}%` }"></div>
      </div>
    </template>

    <!-- 饼图骨架 -->
    <template v-else-if="variant === 'pie'">
      <div class="skeleton-pie">
        <div class="skeleton-pie-circle"></div>
        <div class="skeleton-pie-legend">
          <div v-for="i in 5" :key="i" class="skeleton-legend-item">
            <div class="skeleton-legend-dot"></div>
            <div class="skeleton-legend-text"></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  /** 骨架屏类型 */
  variant: 'stats' | 'chart' | 'pie'
  /** 图表行数 */
  rows?: number
}>()
</script>

<style scoped lang="scss">
.skeleton {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

// ─── 统计卡片骨架 ────────────────────────────────────────────────────────────

.skeleton-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 8px;
}

.skeleton-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.skeleton-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(90deg, rgba(0, 200, 255, 0.1), rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.1));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

.skeleton-lines {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.skeleton-line {
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(90deg, rgba(0, 200, 255, 0.1), rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.1));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;

  &.title {
    width: 60px;
  }

  &.short {
    width: 40px;
    height: 12px;
  }
}

// ─── 图表骨架 ────────────────────────────────────────────────────────────────

.skeleton-chart {
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-bar {
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(90deg, rgba(0, 200, 255, 0.1), rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.1));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

// ─── 饼图骨架 ────────────────────────────────────────────────────────────────

.skeleton-pie {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 16px;
}

.skeleton-pie-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(90deg, rgba(0, 200, 255, 0.1), rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.1));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

.skeleton-pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skeleton-legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  background: rgba(0, 200, 255, 0.2);
}

.skeleton-legend-text {
  width: 60px;
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(90deg, rgba(0, 200, 255, 0.1), rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.1));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

// ─── 动画 ────────────────────────────────────────────────────────────────────

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
