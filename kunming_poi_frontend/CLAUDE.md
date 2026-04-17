# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

昆明市 POI 空间高频模式挖掘 — 前端地图大屏可视化系统。基于 Vue 3 + TypeScript + Vite 构建，核心为高德地图 Loca 可视化与 ECharts 统计图表。

## 开发命令

```bash
# 安装依赖（必须使用 pnpm）
pnpm install

# 本地开发（热更新），同时启动 API 代理到 http://127.0.0.1:8000
pnpm dev

# 类型检查 + 生产构建
pnpm build

# 预览生产包
pnpm preview
```

## 技术架构

### 核心依赖
- **地图**: 高德地图 JS API 2.0 + Loca 空间可视化 API (`@amap/amap-jsapi-loader`)
- **图表**: ECharts 6.x（不支持 ECharts 5，需要注意版本差异）
- **HTTP**: Axios，统一代理到 FastAPI 后端
- **自适应**: 基于 CSS Transform Scale 方案，以 1920x1080 为基准画布

### 目录结构
```
src/
├── api/index.ts            # Axios 封装与接口类型定义
├── components/
│   ├── App.vue             # 大屏主布局（三栏：左|中|右）
│   ├── MapView.vue         # 地图渲染宿主（热力图 + 散点 + 卫星底图）
│   ├── AutofitContainer.vue # 屏幕自适应容器
│   ├── ScreenContainer.vue  # 左右面板定位容器
│   ├── LeftTop.vue         # POI/模式/实例统计概览
│   ├── LeftCenter.vue      # 类别统计饼图
│   ├── LeftBottom.vue      # 行政区划统计
│   ├── RightTop.vue        # FPI 高频模式排行榜
│   ├── RightBottom.vue     # 模式详情/词云
│   ├── StatsPanel.vue      # 统计卡片组件
│   ├── FpiRanking.vue      # FPI 排行榜 ECharts 封装
│   ├── CountUp.vue         # 数字滚动动画
│   ├── SvgAnimate.vue     # SVG 路径流光动画
│   └── ...
├── composables/
│   └── useAMap.ts          # 高德地图懒加载单例
├── hooks/
│   └── useEChartsAutoCarousel.ts
├── utils/
│   └── autofit.ts          # 大屏自适应工具类
├── config/
│   └── amap.ts             # 高德 Key 配置（需自行填写）
└── style.css               # 全局深色主题样式
```

### 布局架构

大屏采用三层叠加结构：
1. **底层**: 全屏高德地图（z-index: 1）
2. **中层**: 装饰层 + 流光边框（z-index: 2-4）
3. **顶层**: 1920x1080 UI 面板容器，CSS Scale 自适应缩放（z-index: 5+）

地图中心点: `[102.7184, 25.0406]`（昆明市）

### 组件通信

- `App.vue` 持有全局状态，通过 props 向下传递数据
- `RightTop` 点击模式卡片 → 触发 `onPatternClick` → 调用 `MapView.renderPattern(patternId)`
- `MapView` 通过 `defineExpose({ renderPattern })` 暴露方法供父组件调用

### API 层

所有接口定义在 `src/api/index.ts`，通过 Vite proxy 转发到 FastAPI 后端：

| 接口方法 | 路径 | 用途 |
|---------|------|------|
| fetchGlobalSummary | GET /api/global-summary | POI/模式/实例总数 |
| fetchCategoryStats | GET /api/category-stats | 类别统计 |
| fetchDistrictSummary | GET /api/district-summary | 行政区划统计 |
| fetchPatternInstances | GET /api/pattern-instances/{id} | 模式下 POI 实例 |
| fetchHeatmapData | GET /api/poi-heatmap-data | 热力图数据 |
| fetchFpiRanking | GET /api/fpi-ranking | FPI 排行榜 |

## 高德地图配置

`src/config/amap.ts` 中需要配置有效的 Key 和安全密钥，否则地图无法加载。申请地址: https://console.amap.com/

## 类别颜色映射

MapView.vue 中预定义了 9 种 POI 类别颜色：
- 购物消费: `#FF6B6B`
- 科教文化: `#4ECDC4`
- 医疗保健: `#45B7D1`
- 汽车相关: `#FFA07A`
- 生活服务: `#98D8C8`
- 交通设施: `#F7DC6F`
- 餐饮美食: `#BB8FCE`
- 休闲娱乐: `#F8B739`
- 运动健身: `#52C41A`

## 关键实现细节

- AMap 使用单例模式加载，通过 `useAMap()` composable 避免重复请求
- 热力图使用 `AMap.HeatMap` 插件，散点使用 `Loca.ScatterLayer`
- 地图样式偏好缓存到 `localStorage` 的 `mapStyleKey` 字段
- ECharts 图表自动轮播通过 `useEChartsAutoCarousel` hook 实现
