<!--
  左侧顶部卡片 - 总体态势概览
  展示 POI 总量、挖掘模式数、模式实例数三项核心指标，
  以及类目分布和区域覆盖的 IconText2 卡片
  @author Hackerdallas
-->
<template>
  <BasicContainer title="总体态势感知">
    <!-- 三项核心指标 -->
    <div class="stat-row">
      <div class="stat-item relative">
        <IconText1 :icon="icon1" label="POI 总量" :value="displayStats[0]?.value || '—'" unit="" />
      </div>
      <div class="stat-item v-line-left relative">
        <IconText1 :icon="icon2" label="挖掘模式数" :value="displayStats[1]?.value || '—'" unit="" />
      </div>
      <div class="stat-item v-line-left relative">
        <IconText1 :icon="icon3" label="模式实例数" :value="displayStats[2]?.value || '—'" unit="" />
      </div>
    </div>

    <!-- 分隔线 -->
    <div class="divider-wrapper">
      <div class="h-line-left"></div>
    </div>

    <!-- 类目 / 区域 IconText2 -->
    <div class="icon-row">
      <div class="icon-item">
        <IconText2 :icon="icon4" label="类目分布" :value="categoryCount" unit="类" />
      </div>
      <div class="icon-item">
        <IconText2 :icon="icon5" label="区域覆盖" :value="districtCount" unit="区" />
      </div>
    </div>
  </BasicContainer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BasicContainer from './BasicContainer.vue'
import IconText1 from './IconText1.vue'
import IconText2 from './IconText2.vue'

const icon1 = new URL('@/assets/icon/i-1.svg', import.meta.url).href
const icon2 = new URL('@/assets/icon/i-2.svg', import.meta.url).href
const icon3 = new URL('@/assets/icon/i-3.svg', import.meta.url).href
const icon4 = new URL('@/assets/icon/i-4.svg', import.meta.url).href
const icon5 = new URL('@/assets/icon/i-5.svg', import.meta.url).href

interface StatItem { label: string; value: string | number }

const props = defineProps<{
  stats?: StatItem[]
  categoryCount?: number
  districtCount?: number
}>()

const displayStats = computed(() => props.stats ?? [
  { label: 'POI 总量', value: '—' },
  { label: '挖掘模式数', value: '—' },
  { label: '模式实例数', value: '—' },
])

const categoryCount = computed(() => props.categoryCount ?? 0)
const districtCount = computed(() => props.districtCount ?? 0)
</script>

<style scoped lang="scss">
.stat-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-top: 8px;
}
.stat-item {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
.divider-wrapper {
  padding: 12px 8px;
}
.icon-row {
  padding: 0 8px 16px 8px;
  display: flex;
  flex-direction: row;
  gap: 8px;
}
.icon-item {
  flex: 1;
  height: 75px;
}
.v-line-left {
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10%;
    height: 80%;
    width: 1px;
    background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA6 50%, rgba(102, 177, 186, 0) 100%);
  }
}
.h-line-left {
  height: 1px;
  background: linear-gradient(90deg, rgba(102, 177, 186, 0) 0%, #539BA6 50%, rgba(102, 177, 186, 0) 100%);
}
</style>
