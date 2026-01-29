# 演示说明

## 演示步骤

1. 启动 PostgreSQL 数据库
```bash
docker-compose up -d
```

2. 运行市场发现模块
```bash
python -m src.indexer.discovery
```

3. 启动链上监听器
```bash
python -m src.indexer.listener
```

4. 启动 API 服务
```bash
python -m src.main
```

5. 查询大单数据
```bash
curl http://localhost:8000/api/whales/live
```

## 预期输出

运行监听器后，控制台会打印类似信息：
```
开始监听链上交易...
🚨 巨鲸警报! will-trump-win: 5000 USD
🚨 巨鲸警报! trump-nomination: 3200 USD
```

API 返回示例：
```json
{
  "whales": [
    {
      "tx_hash": "0x...",
      "market_slug": "will-trump-win",
      "amount_usd": 5000,
      "side": "BUY",
      "outcome": "YES",
      "timestamp": "2025-01-29T10:30:00Z"
    }
  ]
}
```

## 截图

![功能截图](screenshots/demo.png)

## 演示数据

使用的示例市场/交易哈希：
- Market: `will-there-be-another-us-government-shutdown-by-january-31`
- Tx: `0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946`
