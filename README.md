# Insider Hunter - Polymarket 政治突发事件内幕猎手

> 基于 Polymarket 链上数据的大单监控与内幕分析系统

## 项目简介

Insider Hunter 是一个实时监控 Polymarket 政治类预测市场的工具，通过链上数据分析识别大额交易（鲸鱼活动），并利用 AI 分析交易时间与新闻发布时间的关系，发现可能的内幕交易行为。

## 技术架构

```
┌─────────────────┐     ┌─────────────────┐
│  Polygon RPC    │     │   Gamma API     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
    ┌─────────────────────────────────┐
    │         Indexer 模块            │
    │  (链上监听 / 交易解码 / 市场发现) │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │          PostgreSQL             │
    │  (markets/trades/profiles/alerts)│
    └────────────────┬────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐    ┌────────────┐    ┌──────────┐
│Profiler│    │   Agent    │    │   API    │
│(画像)  │    │(内幕分析)   │    │(FastAPI) │
└────────┘    └─────┬──────┘    └──────────┘
                    │
                    ▼
              ┌───────────┐
              │DeepSeek V3│
              └───────────┘
```

**技术栈**：
- 后端框架：FastAPI + Uvicorn
- 数据库：PostgreSQL 15 + SQLAlchemy 2.0 (异步)
- 链上交互：Web3.py
- AI 分析：DeepSeek V3 (OpenAI 兼容接口)

## 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose
- 有效的 Polygon RPC URL
- DeepSeek API Key

### 安装步骤

1. 克隆仓库
```bash
git clone <repo-url>
cd insider-hunter
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入你的配置
```

3. 启动数据库
```bash
docker-compose up -d
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 运行项目
```bash
python -m src.main serve
```

### 运行命令

```bash
# 启动 API 服务 (默认端口 8000)
python -m src.main serve

# 回填历史数据 (默认 6 个月)
python -m src.main backfill

# 回填指定月数的历史数据
python -m src.main backfill 3

# 刷新交易者画像
python -m src.main refresh-profiles

# 执行内幕分析扫描
python -m src.main scan-insider
```

### 历史数据回填

首次运行时，建议先回填历史数据以获得更完整的分析：

```bash
# 回填近 6 个月数据（推荐）
python -m src.main backfill 6

# 回填近 3 个月数据（更快）
python -m src.main backfill 3
```

**注意事项**：
- 回填 6 个月数据可能需要数小时，取决于 RPC 速度
- 建议在后台运行：`nohup python -m src.main backfill 6 > backfill.log 2>&1 &`
- 回填过程支持断点续传，中断后重新运行会跳过已处理的交易

## 功能说明

### 1. 大单实时监控
- 监听 Polymarket CTF Exchange 的 OrderFilled 事件
- 自动标记金额 > 10,000 USD 的大单
- 实时控制台警报

### 2. 交易者画像
- 统计交易者胜率（基于已结算市场）
- 自动分类：聪明钱（胜率>90%）/ 笨蛋钱（胜率<30%）/ 普通
- 胜率排行榜

### 3. 内幕分析 Agent
- 扫描大单交易
- 调用 DeepSeek V3 搜索相关新闻
- 对比交易时间与新闻时间
- 生成内幕嫌疑评分

### 4. REST API
| 接口 | 描述 |
|------|------|
| GET /api/whales/live | 实时大单列表 |
| GET /api/insider/alerts | 内幕分析警报 |
| GET /api/markets | 市场列表 |
| GET /api/market/{slug} | 市场详情 |
| GET /api/traders/leaderboard | 胜率排行榜 |
| GET /api/trader/{address} | 交易者画像 |
| POST /api/insider/analyze | 触发内幕分析 |

## 数据来源

- **链上数据**：Polygon 网络 CTF Exchange 合约事件
- **市场元数据**：Gamma API (https://gamma-api.polymarket.com)
- **新闻搜索**：DeepSeek V3 AI 模型

## 项目结构

```
insider-hunter/
├── docker-compose.yml       # PostgreSQL 容器
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── src/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── db.py                # 数据库连接
│   ├── models.py            # ORM 模型
│   ├── indexer/             # 链上数据模块
│   │   ├── discovery.py     # 市场发现
│   │   ├── decoder.py       # 交易解码
│   │   └── listener.py      # 链上监听
│   ├── profiler/            # 交易者画像模块
│   │   └── analyzer.py      # 画像分析
│   ├── agent/               # AI 分析模块
│   │   └── insider.py       # 内幕分析
│   └── api/                 # API 模块
│       └── routes.py        # 路由定义
└── docs/                    # 项目文档
```

## 团队成员

- [待填写]

## License

MIT
