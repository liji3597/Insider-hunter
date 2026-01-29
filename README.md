# Insider Hunter

Polymarket 政治/突发事件内幕猎手 - 实时监控大额交易并分析潜在内幕交易行为。

## 项目简介

监控 Polymarket 政治类市场的链上交易，捕捉大额交易（鲸鱼活动），并通过 AI 分析交易时间与新闻发布时间的关系，识别潜在的内幕交易行为。

## 技术架构

- **后端**: Python + FastAPI
- **数据库**: PostgreSQL
- **链上数据**: Web3.py + Polygon RPC
- **AI 分析**: OpenAI API

## 快速开始

### 环境要求
- Python 3.10+
- Docker & Docker Compose
- 有效的 Polygon RPC URL

### 安装步骤

1. 克隆仓库
```bash
git clone <repo-url>
cd insider-hunter
```

2. 启动数据库
```bash
docker-compose up -d
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入你的 RPC URL 和 API Key
```

5. 运行项目
```bash
python -m src.main
```

## 功能说明

- 实时监控 Polymarket 政治类市场交易
- 大单交易（>$1000）自动标记和报警
- AI 分析交易与新闻时间差
- RESTful API 接口

## 数据来源

- 链上数据: Polygon 网络 CTF Exchange 合约
- 市场元数据: Gamma API

## 团队成员

- [Your Name]
