<!--
  毛玻璃卡片装饰组件
  @description 径向渐变边框 + 模糊背景的科技感容器
  @author Hackerdallas
-->
<template>
  <div class="glass-card-container" :style="{ width: typeof width === 'number' ? `${width}px` : width }">
    <div class="card-border-wrapper">
      <!-- 径向渐变边框层 -->
      <div class="radial-border"></div>
      
      <!-- 主体内容区 -->
      <div class="card-main-body">
        <!-- 标题栏 -->
        <div v-if="title" class="card-title-bar">
          <div class="title-icon">
            <img :src="iconUrl" v-if="iconUrl" />
          </div>
          <div class="title-text">{{ title }}</div>
        </div>
        
        <!-- 内容插槽 -->
        <div class="card-content-area" :style="{ padding }">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: { type: String, default: '' },
  width: { type: [Number, String], default: '100%' },
  padding: { type: String, default: '24px 12px' },
  iconUrl: { type: String, default: '' }
})
</script>

<style scoped>
.glass-card-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  box-sizing: border-box;
}

.card-border-wrapper {
  width: 100%;
  height: 100%;
  padding: 3px;
  box-sizing: border-box;
  border-radius: 24px;
  overflow: hidden;
  position: relative;
}

/* 径向渐变边框效果 */
.card-border-wrapper::before {
  border-radius: 24px;
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
  margin: auto;
  width: 100%;
  height: 100%;
  background: radial-gradient(80% 50% at 50% 100%, #4C99BF 0%, rgba(50, 88, 108, 0.2) 99%, rgba(50, 88, 108, 0.2) 100%);
}

.card-main-body {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  z-index: 10;
  border-radius: 24px;
  box-sizing: border-box;
  backdrop-filter: blur(24px);
  border: 2px solid rgba(166, 255, 255, 0.2);
  box-shadow: 0px 12px 8px 0px rgba(12, 19, 18, 0.15);
  background: rgba(6, 20, 38, 0.25);
  transition: border-color 0.3s ease;
}

.card-main-body:hover {
  border-color: rgba(166, 255, 255, 0.4);
}

.card-title-bar {
  display: flex;
  align-items: center;
  padding: 16px 20px 12px;
  gap: 12px;
  border-bottom: 1px solid rgba(166, 255, 255, 0.1);
}

.title-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.title-text {
  font-family: 'YouShe', serif;
  text-align: left;
  background: linear-gradient(180deg, #D2FEFF 0%, #95F1F7 53%, #DFFFFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 18px;
  letter-spacing: 1px;
}

.card-content-area {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: auto;
}
</style>
