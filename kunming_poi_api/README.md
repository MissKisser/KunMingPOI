# KunmingPOI-API

昆明市 POI 空间同位模式挖掘系统后端 API 服务，为前端大屏可视化提供地理点位透传与特征榜单查询。

## 技术栈

- **框架**: FastAPI + SQLAlchemy ORM
- **数据库**: MySQL
- **运行服务**: Uvicorn

## 数据表结构

### poi_base (POI基础点位表)
| 字段 | 类型 | 说明 |
|------|------|------|
| poi_id | Integer | 主键，自增 |
| poi_name | String(255) | POI名称 |
| category_name | String(100) | 类别名称，带索引 |
| lng | Float | 经度 |
| lat | Float | 纬度 |
| district | String(50) | 所属区县 |

### fpi_patterns (空间同位模式表)
| 字段 | 类型 | 说明 |
|------|------|------|
| pattern_id | Integer | 主键，自增 |
| pattern_name | String(255) | 模式名称，唯一 |
| pattern_display_name | String(500) | 显示名称 |
| fpi_score | Float | FPI频繁度得分，带索引 |
| pattern_order | Integer | 排序序号 |
| instance_count | Integer | 实例数量 |

### pattern_instances (模式实例表)
| 字段 | 类型 | 说明 |
|------|------|------|
| instance_id | Integer | 主键，自增 |
| pattern_id | Integer | 关联模式ID，带索引 |
| poi_id_list | JSON | 该实例包含的POI ID列表 |

### category_mapping (类别映射表)
| 字段 | 类型 | 说明 |
|------|------|------|
| category_id | Integer | 主键，自增 |
| category_name | String(100) | 类别名称，唯一 |
| category_code | String(1) | 类别代码（A-Z），唯一 |
| category_order | Integer | 排序序号 |
| description | String(500) | 类别描述 |
| poi_count | Integer | 该类别POI数量 |

### district_statistics (区县统计表)
| 字段 | 类型 | 说明 |
|------|------|------|
| stat_id | Integer | 主键，自增 |
| district | String(50) | 区县名称，带索引 |
| category_name | String(100) | 类别名称 |
| poi_count | Integer | POI数量 |
| pattern_count | Integer | 模式数量 |

## API 接口

### 全局数据

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/global-summary` | GET | - | 返回系统核心监控指标（POI总数、模式总数、实例总数、最大FPI值） |
| `/api/category-stats` | GET | - | 返回各大类基础统计，用于前端玫瑰图 |
| `/api/district-summary` | GET | - | 各行政区维度汇总数据 |

### POI 数据

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/all-pois` | GET | `limit`, `offset`, `category_code`, `district` | 基础点位池，支持条件过滤 |
| `/api/poi-heatmap-data` | GET | `limit` | POI热力图数据 |

### 模式数据

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/fpi-ranking` | GET | `limit` | FPI频繁度排行榜 |
| `/api/pattern-coordinates/{pattern_id}` | GET | `pattern_id` | 返回特定模式的高维经纬度空间节点集合 |
| `/api/pattern-instances/{pattern_id}` | GET | `pattern_id` | 返回模式实例分组数据，包含完整POI信息 |
| `/api/pattern-wordcloud` | GET | - | 高频模式子集共现规律，用于词云图 |

### 区域统计

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/district-stats` | GET | - | 各区县POI分布与计算热度统计 |

## 安装与运行

### 1. 安装依赖

```bash
cd kunming_poi_api
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `database.py` 中的数据库连接配置：

```python
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:{password}@127.0.0.1:3306/kunming_poi"
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 4. 访问 API 文档

服务启动后访问：http://127.0.0.1:8000/docs

## 测试

```bash
python test_api.py
```

## 作者

Hackerdallas
