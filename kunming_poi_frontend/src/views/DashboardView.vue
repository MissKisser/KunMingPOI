<!--
  态势感知大屏视图
  原主屏功能，包含地图和两侧数据看板
  @author Hackerdallas
-->
<template>
  <div class="dashboard">
    <!-- 底层：全屏地图 -->
    <section class="map-background">
      <MapView ref="mapView" />
    </section>

    <!-- 自适应逻辑容器 -->
    <AutofitContainer>
      <!-- 背景氛围层 -->
      <div class="dot-bg"></div>
      <div class="border-bg"></div>

      <!-- 装饰层：全屏流光回流线 -->
      <div class="perimeter-flow">
        <SvgAnimate class="flow-p top-line-l" :width="960" :height="78" color="#30DCFF" :stroke-width="3" path="M1 1L30.5 49.5H656L668 62H696.5L706.5 77H960" />
        <SvgAnimate class="flow-p top-line-r" :width="960" :height="78" color="#30DCFF" :stroke-width="3" path="M959 1L927 49.5H301.5L289.5 62H261L251 77H0" />
        <SvgAnimate class="flow-p left-side-line" :width="944" :height="1002" :duration="5" color="#30DCFF" :stroke-width="3" path="M639.162 1H26.4865L1 26.4364V969.08L26.4865 1001H945" />
        <SvgAnimate class="flow-p right-side-line" :width="944" :height="1002" :duration="5" color="#30DCFF" :stroke-width="3" path="M305.838 1H918.513L944 26.4364V969.08L918.513 1001H0" />
        <img class="bottom-decoration" src="@/assets/icon/bg-2.svg" alt="decoration">
      </div>

      <header class="float-header" :class="[isInit ? 'active' : '']">
        <div class="title">昆明空间高频模式态势感知</div>
      </header>

      <div class="ui-overlay">
        <!-- 左侧面板 -->
        <ScreenContainer position="left" :is-init="isInit">
          <LeftTop :stats="overviewStats" :categoryCount="categoryCount" :districtCount="districtCount" />
          <LeftCenter :pieData="pieData" />
          <LeftBottom ref="leftBottom" />
        </ScreenContainer>

        <!-- 右侧面板 -->
        <ScreenContainer position="right" :is-init="isInit">
          <RightTop @pattern-click="onPatternClick" />
          <RightBottom />
        </ScreenContainer>
      </div>
    </AutofitContainer>

    <!-- 全局 Toast 提示 -->
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import MapView from '../components/MapView.vue'
import LeftTop from '../components/LeftTop.vue'
import LeftCenter from '../components/LeftCenter.vue'
import LeftBottom from '../components/LeftBottom.vue'
import RightTop from '../components/RightTop.vue'
import RightBottom from '../components/RightBottom.vue'
import ScreenContainer from '../components/ScreenContainer.vue'
import SvgAnimate from '../components/SvgAnimate.vue'
import AutofitContainer from '../components/AutofitContainer.vue'
import Toast from '../components/Toast.vue'
import { useOverviewStore, useUIStore } from '../stores'
import { storeToRefs } from 'pinia'
import { MAP_CONFIG } from '../constants'

const overviewStore = useOverviewStore()
const uiStore = useUIStore()

const { initialized: isInit } = storeToRefs(uiStore)
const { overviewStats, pieData, categoryCount, districtCount, districtSummary } = storeToRefs(overviewStore)

const leftBottom = ref<InstanceType<typeof LeftBottom> | null>(null)
const mapView = ref<InstanceType<typeof MapView> | null>(null)

async function onPatternClick(patternId: number) {
  mapView.value?.renderPattern(patternId)
}

onMounted(async () => {
  uiStore.startTimeUpdater()

  setTimeout(() => {
    uiStore.setInitialized(true)
  }, MAP_CONFIG.HEADER_DELAY)

  try {
    await overviewStore.fetchAll()
    leftBottom.value?.renderDistrictStats(districtSummary.value)
  } catch (err) {
    console.warn('后端总览接口请求失败', err)
  }
})

onBeforeUnmount(() => {
  uiStore.stopTimeUpdater()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
  height: 100%;
  background: #060d18;
  overflow: hidden;
  position: relative;
}

.map-background {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.perimeter-flow {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}
.flow-p { position: absolute; }
.top-line-l { top: 24px; left: 0; }
.top-line-r { top: 24px; right: 0; }
.left-side-line { left: 14px; top: 64px; height: calc(100% - 68px); width: 50%; }
.right-side-line { right: 14px; top: 64px; height: calc(100% - 68px); width: 50%; text-align: right; }

.bottom-decoration {
  position: absolute;
  bottom: 16px;
  opacity: .6;
  width: 1400px;
  left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
}

.dot-bg {
  pointer-events: none;
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  background: url('@/assets/icon/bg-dot.png');
  background-size: 20px 20px;
  opacity: 0.15;
  z-index: 1;
}

.border-bg {
  position: absolute;
  inset: 0;
  padding: 64px 15px 4px 15px;
  pointer-events: none;
  z-index: 30;
  &::before {
    content: '';
    display: block;
    width: 100%;
    height: 100%;
    background: url('@/assets/icon/border-bg.png') no-repeat;
    background-size: 100% 100%;
    opacity: 0.6;
  }
}

.float-header {
  position: absolute;
  top: -105px;
  left: 0;
  width: 100%;
  height: 105px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  pointer-events: none;
  transition: all 0.5s linear;
  background: url('@/assets/icon/header-bg.png') no-repeat;
  background-size: 100% 100%;
}

.float-header.active {
  top: -20px;
}

.title {
  font-family: 'YouShe', serif;
  letter-spacing: 4px;
  background: linear-gradient(180deg, #E3FFFE 27%, #ACFFFD 75%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 44px;
  position: relative;
  top: 2px;
  text-shadow: 0 0 20px rgba(62, 229, 255, 0.4);
}

.ui-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 1920px;
  height: 1080px;
  z-index: 5;
  pointer-events: none;
}
</style>
