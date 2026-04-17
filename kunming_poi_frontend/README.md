# kunming_poi_frontend

> 昆明市 POI 空间高频模式挖掘 — 前端地图大屏可视化
>
> 作者：Hackerdallas

## 技术栈

| 职责 | 技术 |
|------|------|
| 宿主框架 | Vue 3 + Vite + TypeScript |
| 地图底座 | 高德地图 JS API 2.0 + Loca 空间可视化 API |
| 统计图表 | ECharts 5.x |
| HTTP 客户端 | Axios |
| 包管理器 | pnpm |

## 包管理器

本项目统一使用 **pnpm**，禁止混用 npm / yarn。

## 环境要求

- Node.js >= 18
- pnpm >= 9

## 快速启动

```bash
# 安装依赖
pnpm install

# 本地开发（热更新）
pnpm dev

# 构建生产包
pnpm build

# 预览生产包
pnpm preview
```

## 高德地图 Key 配置

在 `src/config/amap.ts` 中填写你的高德地图 Web JS API Key 与安全密钥：

```ts
export const AMAP_KEY = 'YOUR_KEY_HERE'
export const AMAP_SECRET = 'YOUR_SECRET_HERE'
```

> 申请地址：[https://console.amap.com/](https://console.amap.com/)

## 后端接口

默认代理到 `http://127.0.0.1:8000`（FastAPI），由 `vite.config.ts` 的 proxy 配置统一转发。

## 目录结构

```
src/
├── config/         # 全局配置（高德 Key 等）
├── components/
│   ├── MapView.vue         # 高德地图 + Loca 渲染宿主
│   ├── FpiRanking.vue      # 右侧 FPI 排行榜（ECharts）
│   └── StatsPanel.vue      # 左侧统计面板（ECharts）
├── composables/
│   └── useAMap.ts          # 高德地图懒加载 Hook
├── api/
│   └── index.ts            # Axios 封装 + 接口定义
├── App.vue                 # 大屏整体布局
├── main.ts
└── style.css               # 全局深色样式
```
