# 演示说明

## 演示环境准备

### 1. 启动数据库
```bash
docker-compose up -d
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入：
# - POLYGON_RPC_URL: 你的 Polygon RPC 地址
# - DEEPSEEK_API_KEY: DeepSeek API 密钥
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动服务
```bash
python -m src.main serve
```

## 演示步骤

### 步骤 1: 检查服务状态
```bash
curl http://localhost:8000/api/health
```

预期输出：
```json
{"status": "ok", "service": "insider-hunter"}
```

### 步骤 2: 查看市场列表
```bash
curl http://localhost:8000/api/markets?limit=5
```

### 步骤 3: 查看大单列表
```bash
curl http://localhost:8000/api/whales/live?limit=10
```

预期输出：
```json
{
    "total": 150,
    "data": [
        {
            "tx_hash": "0x...",
            "market_slug": "will-trump-win",
            "maker": "0x1234...",
            "side": "BUY",
            "outcome": "YES",
            "price": 0.65,
            "amount_usd": 15000.00,
            "timestamp": "2026-01-30T10:30:00"
        }
    ]
}
```

### 步骤 4: 触发内幕分析
```bash
curl -X POST "http://localhost:8000/api/insider/analyze?limit=3"
```

预期输出：
```json
{
    "analyzed": 3,
    "suspect_count": 1,
    "message": "已分析 3 笔交易，发现 1 笔可疑交易"
}
```

### 步骤 5: 查看内幕警报
```bash
curl "http://localhost:8000/api/insider/alerts?suspect_only=true"
```

### 步骤 6: 查看交易者排行榜
```bash
curl "http://localhost:8000/api/traders/leaderboard?limit=10&min_trades=5"
```

## 预期输出

### 控制台日志
启动后控制台会显示：
```
🚀 Insider Hunter 启动中...
✓ 数据库初始化完成
✓ 同步了 50 个新市场，共 150 个活跃市场
✓ 链上监听器已启动
✓ Insider Hunter 启动完成!
  API 地址: http://localhost:8000
  文档地址: http://localhost:8000/docs
```

当检测到大单时：
```
🚨 巨鲸警报! will-trump-win [YES]: $15,000.00 USD (BUY)
```

## 截图

![功能截图](screenshots/demo.png)

## 演示数据

使用的示例市场/交易哈希：
- Market: `will-there-be-another-us-government-shutdown-by-january-31`
- Tx: `0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946`

## API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。
