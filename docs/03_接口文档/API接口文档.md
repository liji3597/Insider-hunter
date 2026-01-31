# Insider Hunter API 接口文档

## 概述

Insider Hunter 提供 RESTful API 用于查询 Polymarket 大单交易、市场信息、交易者画像和内幕分析。

- **Base URL**: `http://localhost:8000`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

---

## 通用响应格式

### 成功响应
```json
{
  "total": 100,
  "data": [...]
}
```

### 错误响应
```json
{
  "detail": "错误描述"
}
```

### HTTP 状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

---

## 接口列表

### 1. 健康检查

**GET** `/api/health`

检查服务运行状态。

**请求参数**: 无

**响应示例**:
```json
{
  "status": "ok",
  "service": "insider-hunter"
}
```

---

### 2. 市场列表

**GET** `/api/markets`

获取 Polymarket 市场列表。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 50 | 返回数量 (1-200) |
| offset | int | 否 | 0 | 偏移量 |
| active_only | bool | 否 | true | 是否只返回活跃市场 |

**响应示例**:
```json
{
  "total": 200,
  "data": [
    {
      "slug": "will-trump-win-2024",
      "question": "Will Trump win the 2024 election?",
      "category": "Politics",
      "resolved": false,
      "resolution_outcome": null,
      "active": true,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

### 3. 市场详情

**GET** `/api/market/{slug}`

获取单个市场的详细信息和交易统计。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| slug | string | 市场唯一标识 |

**响应示例**:
```json
{
  "slug": "will-trump-win-2024",
  "question": "Will Trump win the 2024 election?",
  "condition_id": "0x...",
  "yes_token_id": "12345...",
  "no_token_id": "67890...",
  "category": "Politics",
  "resolved": false,
  "resolution_outcome": null,
  "active": true,
  "stats": {
    "trade_count": 1500,
    "total_volume": 250000.50,
    "whale_count": 45
  },
  "recent_trades": [
    {
      "tx_hash": "0x...",
      "maker": "0x...",
      "side": "BUY",
      "outcome": "YES",
      "amount_usd": 5000.00,
      "timestamp": "2024-01-20T14:30:00"
    }
  ]
}
```

---

### 4. 大单列表

**GET** `/api/whales/live`

获取实时大单交易列表（amount_usd >= 1000 USD）。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 20 | 返回数量 (1-100) |
| offset | int | 否 | 0 | 偏移量 |
| market_slug | string | 否 | - | 筛选特定市场 |

**响应示例**:
```json
{
  "total": 156,
  "data": [
    {
      "tx_hash": "0xabc123...",
      "market_slug": "will-trump-win-2024",
      "maker": "0x1234...",
      "side": "BUY",
      "outcome": "YES",
      "price": 0.65,
      "size": 10000.0,
      "amount_usd": 6500.00,
      "timestamp": "2024-01-20T14:30:00"
    }
  ]
}
```

---

### 5. 交易者排行榜

**GET** `/api/traders/leaderboard`

获取交易者胜率排行榜。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 20 | 返回数量 (1-100) |
| min_trades | int | 否 | 5 | 最小交易次数 |
| trader_type | string | 否 | - | 筛选类型: smart_money/dumb_money/normal |

**响应示例**:
```json
{
  "data": [
    {
      "address": "0x1234...",
      "total_trades": 150,
      "win_rate": 0.72,
      "total_pnl": 25000.50,
      "avg_trade_size": 500.00,
      "trader_type": "smart_money",
      "last_trade_at": "2024-01-20T14:30:00"
    }
  ]
}
```

---

### 6. 交易者详情

**GET** `/api/trader/{address}`

获取单个交易者的详细画像。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| address | string | 钱包地址 (0x...) |

**响应示例**:
```json
{
  "address": "0x1234...",
  "total_trades": 150,
  "win_rate": 0.72,
  "total_pnl": 25000.50,
  "avg_trade_size": 500.00,
  "trader_type": "smart_money",
  "favorite_markets": [
    {"slug": "will-trump-win-2024", "trade_count": 45}
  ],
  "recent_trades": [
    {
      "tx_hash": "0x...",
      "market_slug": "will-trump-win-2024",
      "side": "BUY",
      "outcome": "YES",
      "amount_usd": 5000.00,
      "timestamp": "2024-01-20T14:30:00"
    }
  ]
}
```

---

### 7. 内幕警报列表

**GET** `/api/insider/alerts`

获取 AI 分析的内幕交易警报。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| suspect_only | bool | 否 | false | 是否只返回可疑交易 |
| limit | int | 否 | 20 | 返回数量 (1-100) |
| offset | int | 否 | 0 | 偏移量 |

**响应示例**:
```json
{
  "total": 25,
  "data": [
    {
      "id": 1,
      "trade_id": 123,
      "tx_hash": "0xabc...",
      "market_slug": "will-trump-win-2024",
      "is_suspect": true,
      "confidence_score": 0.85,
      "reasoning": "该交易者在市场结算前24小时内进行大额单向押注...",
      "analyzed_at": "2024-01-20T15:00:00"
    }
  ]
}
```

---

### 8. 触发内幕分析

**POST** `/api/insider/analyze`

手动触发 AI 内幕交易分析。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 5 | 分析交易数量 (1-20) |

**响应示例**:
```json
{
  "analyzed": 5,
  "suspect_count": 2,
  "message": "已分析 5 笔交易，发现 2 笔可疑交易"
}
```

---

## 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 404 | 资源不存在 | 检查 slug 或 address 是否正确 |
| 422 | 参数验证失败 | 检查参数类型和范围 |
| 500 | 服务器错误 | 查看服务日志 |

---

## 使用示例

### cURL

```bash
# 获取市场列表
curl "http://localhost:8000/api/markets?limit=10"

# 获取大单
curl "http://localhost:8000/api/whales/live?limit=20"

# 触发内幕分析
curl -X POST "http://localhost:8000/api/insider/analyze?limit=5"
```

### Python

```python
import requests

# 获取市场列表
resp = requests.get("http://localhost:8000/api/markets", params={"limit": 10})
markets = resp.json()

# 获取交易者详情
resp = requests.get("http://localhost:8000/api/trader/0x1234...")
trader = resp.json()
```

### JavaScript

```javascript
// 获取大单列表
const response = await fetch('http://localhost:8000/api/whales/live?limit=20');
const whales = await response.json();

// 触发分析
const result = await fetch('http://localhost:8000/api/insider/analyze?limit=5', {
  method: 'POST'
});
```
