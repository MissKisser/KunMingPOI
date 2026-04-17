<!--
  主布局组件
  包含顶部导航栏和路由视图
  @author Hackerdallas
-->
<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">◈</span>
        <span class="brand-text">昆明空间高频模式</span>
      </div>
      <nav class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          <IconDashboard class="link-icon" :size="16" />
          <span>态势感知</span>
        </router-link>
        <router-link to="/patterns" class="nav-link" :class="{ active: $route.path === '/patterns' }">
          <IconNetwork class="link-icon" :size="16" />
          <span>模式分析</span>
        </router-link>
        <router-link to="/districts" class="nav-link" :class="{ active: $route.path === '/districts' }">
          <IconMap class="link-icon" :size="16" />
          <span>区域分析</span>
        </router-link>
        <router-link to="/overview" class="nav-link" :class="{ active: $route.path === '/overview' }">
          <IconChart class="link-icon" :size="16" />
          <span>数据总览</span>
        </router-link>
      </nav>
      <div class="nav-time">
        <span class="time-value">{{ currentTime.split(' ')[1] }}</span>
        <span class="date-value">{{ currentTime.split(' ')[0] }}</span>
        <button class="refresh-btn" @click="handleRefresh" :disabled="isRefreshing" title="刷新数据">
          <IconRefresh :size="14" :class="['refresh-icon', { spinning: isRefreshing }]" />
        </button>
      </div>
    </header>
    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition :name="(route.meta.transition as string) || 'slide-fade'" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { clearApiCache } from '../api/index'
import { IconDashboard, IconNetwork, IconMap, IconChart, IconRefresh } from '../components/icons'

const currentTime = ref('')
const isRefreshing = ref(false)

function updateTime() {
  const now = new Date()
  const dateStr = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
  const timeStr = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
  currentTime.value = `${dateStr} ${timeStr}`
}

async function handleRefresh() {
  if (isRefreshing.value) return
  isRefreshing.value = true

  clearApiCache()
  window.location.reload()
}

let timer: number

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
})

onBeforeUnmount(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.main-layout {
  width: 100vw;
  height: 100vh;
  background: #060d18;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-nav {
  height: 56px;
  background: linear-gradient(180deg, rgba(0, 30, 60, 0.95) 0%, rgba(0, 20, 40, 0.9) 100%);
  border-bottom: 1px solid rgba(0, 200, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  backdrop-filter: blur(10px);
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  font-size: 24px;
  color: #3EE5FF;
  text-shadow: 0 0 10px rgba(62, 229, 255, 0.5);
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(180deg, #E3FFFE 0%, #30DCFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.nav-link:hover {
  color: #fff;
  background: rgba(62, 229, 255, 0.1);
  border-color: rgba(62, 229, 255, 0.3);
}

.nav-link.active {
  color: #3EE5FF;
  background: rgba(62, 229, 255, 0.15);
  border-color: rgba(62, 229, 255, 0.5);
}

.link-icon {
  font-size: 16px;
}

.nav-time {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  padding: 4px 12px;
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 200, 255, 0.2);
  border-radius: 4px;
}

.time-value {
  font-size: 14px;
  font-family: 'MiSans-Demibold', 'Courier New', monospace;
  color: #3EE5FF;
  letter-spacing: 1px;
}

.date-value {
  font-size: 12px;
  color: rgba(0, 200, 255, 0.6);
  letter-spacing: 1px;
}

.refresh-btn {
  margin-left: 12px;
  padding: 4px 8px;
  background: transparent;
  border: 1px solid rgba(0, 200, 255, 0.3);
  border-radius: 4px;
  color: #3EE5FF;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(0, 200, 255, 0.1);
  border-color: rgba(0, 200, 255, 0.5);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.3s;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.25s ease;
}

.scale-fade-enter-from,
.scale-fade-leave-to {
  transform: scale(0.95);
  opacity: 0;
}
</style>
