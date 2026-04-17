# KunMingPOI

昆明市 POI 空间同位模式挖掘系统，基于 30 万余条兴趣点数据进行空间关联模式挖掘，输出 FPI (Frequent Pattern Index) 榜单，为前端大屏可视化提供数据支撑。

## 项目架构

```
KunMingPOI/
├── scripts/                          # 核心算法工作区（Python）
│   ├── BasicToos2025070.py           # 底层引擎：网格邻居检索、高斯核密度
│   ├── FPI_joinless(new_FPI_Joinless).py  # 顶层挖掘：无连接空间模式
│   ├── BasicToos改造修补与避坑记录表.md   # 算法改造文档
│   ├── FPI_joinless_改造记录表.md        # FPI改造文档
│   └── requirements.txt              # Python依赖
├── kunming_poi_api/                  # 后端 API 服务（FastAPI）
│   ├── main.py                       # FastAPI 主程序
│   ├── database.py                   # SQLAlchemy 数据库连接
│   ├── models.py                     # ORM 模型定义
│   ├── requirements.txt              # Python依赖
│   └── README.md                     # API 详细文档
├── kunming_poi_frontend/             # 前端大屏可视化（Vue 3）
│   ├── src/                          # 源代码目录
│   ├── package.json                  # npm 包配置
│   ├── vite.config.ts                # Vite 构建配置
│   ├── .env.example                  # 环境变量示例
│   └── README.md                     # 前端详细文档
└── openlayer+threejs+720/            # 720° 全景可视化模块（独立项目）
```

## 数据流向

```
原始 CSV → 数据预处理 → .data 网格格式
    ↓
空间挖掘算法 → fpi_patterns.csv + pattern_instances.json
    ↓
MySQL 数据库 → FastAPI REST API
    ↓
Vue 3 前端 → 高德地图 + ECharts 可视化
```

## 技术栈

| 模块 | 技术 |
|------|------|
| 算法引擎 | Python + pandas + psutil + multiprocessing |
| 后端服务 | FastAPI + SQLAlchemy + MySQL |
| 前端大屏 | Vue 3 + TypeScript + Vite + 高德地图 + ECharts |

## 快速启动

### 前端

```bash
cd kunming_poi_frontend
pnpm install
pnpm dev          # 开发服务器，代理 API 到 http://127.0.0.1:8000
pnpm build        # 生产构建
```

### 后端

```bash
cd kunming_poi_api
pip install -r requirements.txt
python main.py    # 或 uvicorn main:app --reload --port 8000
```

### 算法运行

```bash
cd scripts
pip install -r requirements.txt
python FPI_joinless(new_FPI_Joinless).py  # 执行空间挖掘
```

## 关键配置

- **高德地图 Key**: `kunming_poi_frontend/src/config/amap.ts` - 需填写有效的 Key
- **数据库连接**: `kunming_poi_api/database.py` 中的 `SQLALCHEMY_DATABASE_URL`
- **昆明市地图中心**: `[102.7184, 25.0406]`

## 核心算法说明

### FPI 空间同位模式挖掘

系统采用无连接 (Joinless) 算法进行空间关联模式挖掘：

1. **网格化预处理**: 将原始 POI 数据映射到虚拟网格坐标系
2. **星型邻居检索**: 基于距离阈值构建空间邻接关系
3. **频繁模式挖掘**: 通过多阶扩展计算 FPI (Frequent Pattern Index)
4. **多进程并行**: 利用 multiprocessing 实现多核并行加速

详细算法改造记录见 `scripts/` 目录下的文档。

## API 接口概览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/global-summary` | GET | POI/模式/实例总数 |
| `/api/fpi-ranking` | GET | FPI 排行榜 |
| `/api/poi-heatmap-data` | GET | 热力图数据 |
| `/api/pattern-instances/{id}` | GET | 模式实例详情 |

完整 API 文档见 `kunming_poi_api/README.md`。

## 前端功能

- **地图渲染**: 高德地图 + Loca 空间可视化（热力图、散点图层）
- **统计图表**: ECharts 玫瑰图、排行榜、词云
- **自适应布局**: 基于 CSS Transform 的 1920x1080 大屏适配
- **实时交互**: 点击模式卡片触发地图点位高亮

完整前端文档见 `kunming_poi_frontend/README.md`。

## 环境要求

- Python 3.8+
- Node.js 18+
- MySQL 5.7+
- pnpm 9+

## 作者

Hackerdallas

## License

MIT