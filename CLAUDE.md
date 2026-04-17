# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

昆明市 POI 空间同位模式挖掘系统，对 30 万余条兴趣点数据进行空间关联模式挖掘，输出 FPI (Frequent Pattern Index) 榜单，为前端大屏可视化提供数据支撑。

## 项目架构

```
KunmingPOI/
├── scripts/                    # 核心算法工作区（Python）
│   ├── poi_data_converter.py   # 数据预处理：CSV → .data 网格格式
│   ├── BasicToos2025070.py     # 底层引擎：网格邻居检索、高斯核密度
│   └── FPI_joinless(new_FPI_Joinless).py  # 顶层挖掘：无连接空间模式
├── kunming_poi_api/            # 后端 API 服务（FastAPI + SQLAlchemy + MySQL）
├── kunming_poi_frontend/       # 前端大屏可视化（Vue 3 + TypeScript + 高德地图）
├── openlayer+threejs+720/      # 720° 全景可视化模块（独立项目）
├── 01_算法离线处理阶段/         # 算法原理文档
├── 02_数据库搭建与落库阶段/     # 数据库设计文档
├── 03_后端API服务开发阶段/      # 后端开发文档
└── 04_前端地图大屏可视化阶段/    # 前端开发文档
```

## 数据流向

```
原始 CSV → scripts/poi_data_converter.py → .data 格式
    ↓
scripts/FPI_joinless.py → fpi_patterns.csv + pattern_instances.json
    ↓
kunming_poi_api/main.py → 读取 MySQL 数据库暴露 REST API
    ↓
kunming_poi_frontend → 高德地图 + ECharts 可视化渲染
```

## 常用命令

### 前端开发
```bash
cd kunming_poi_frontend
pnpm install
pnpm dev          # 启动开发服务器，代理 API 到 http://127.0.0.1:8000
pnpm build        # 类型检查 + 生产构建
```

### 后端开发
```bash
cd kunming_poi_api
pip install -r requirements.txt
python main.py    # 或 uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 算法运行（需要 pandas, psutil）
```bash
cd scripts
pip install -r requirements.txt
python poi_data_converter.py   # 仅需执行一次，数据预处理
python FPI_joinless(new_FPI_Joinless).py  # 执行空间挖掘
```

## 关键配置

- **高德地图 Key**: `kunming_poi_frontend/src/config/amap.ts` - 需填写有效的 Key 和安全密钥
- **数据库连接**: `kunming_poi_api/database.py` 中的 `SQLALCHEMY_DATABASE_URL`
- **昆明市地图中心**: `[102.7184, 25.0406]`

## 子项目文档

- `kunming_poi_frontend/CLAUDE.md` - 前端详细开发指南
- `kunming_poi_api/README.md` - 后端 API 文档
- `openlayer+threejs+720/README.md` - 720° 全景项目文档
