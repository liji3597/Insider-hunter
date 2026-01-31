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

### 7. AI交易者画像排行榜

**GET** `/api/traders/ai-leaderboard`

获取带AI深度分析的交易者排行榜。只返回已完成AI分析的交易者。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 20 | 返回数量 (1-100) |
| trader_type | string | 否 | - | 筛选类型: smart_money/dumb_money/normal |

**响应示例**:
```json
{
  "data": [
    {
      "address": "0x1234567890abcdef1234567890abcdef12345678",
      "label": "激进型政治预测专家",
      "trader_type": "smart_money",
      "trading_style": "激进",
      "risk_preference": "高",
      "ai_analysis": "该交易者展现出明显的激进风格，以大额交易参与政治预测市场。其92.5%的超高胜率显示出强大的信息优势和判断能力。交易行为特征显示其倾向于在重大政治事件前快速建仓，能够准确把握市场情绪和事件走向。整体来看，这是一位经验丰富、信息优势明显的专业预测者，擅长政治类市场，具有极高的参考价值。",
      "win_rate": 92.5,
      "total_trades": 45,
      "total_volume": 125000.00,
      "avg_trade_size": 2777.78,
      "last_trade_at": "2024-01-30T10:00:00"
    }
  ]
}
```

**响应字段说明**:
- `label`: AI生成的个性化标签（5-10字）
- `trading_style`: 交易风格（激进/稳健/保守/投机/对冲）
- `risk_preference`: 风险偏好（高/中/低）
- `ai_analysis`: AI深度分析文本（150-300字专业评价）

---

### 8. 分析单个交易者（AI）

**POST** `/api/traders/{address}/ai-analyze`

对指定交易者进行AI画像分析。如果已分析过则返回缓存结果（除非使用force_refresh）。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| address | string | 钱包地址 (0x...) |

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| force_refresh | bool | 否 | false | 是否强制重新分析（忽略缓存） |

**响应示例**:
```json
{
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "稳健型政治预测专家",
  "trading_style": "稳健",
  "risk_preference": "中",
  "ai_analysis": "该交易者展现出稳健的投资风格，以中等规模的交易量参与政治预测市场。其89.5%的胜率显示出较强的判断能力和信息优势。交易行为特征显示其倾向于做多（买入YES），且能够准确把握政治事件的走向。整体来看，这是一位经验丰富、决策谨慎的专业预测者，擅长政治类市场，具有较高的可信度。",
  "cached": false
}
```

**错误响应**:
```json
{
  "detail": "交易者不存在或分析失败"
}
```

---

### 9. 批量AI分析交易者

**POST** `/api/traders/batch-ai-analyze`

批量对多个交易者进行AI画像分析。适合首次部署或定期刷新使用。

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 50 | 分析数量 (1-200) |
| min_trades | int | 否 | 5 | 最小交易次数（筛选条件） |
| force_refresh | bool | 否 | false | 是否强制重新分析 |

**响应示例**:
```json
{
  "analyzed": 45,
  "message": "已完成 45 个交易者的AI画像分析",
  "results": [
    {
      "address": "0x1234567890abcdef1234567890abcdef12345678",
      "label": "激进型政治预测专家",
      "ai_analysis": "...",
      "trading_style": "激进",
      "risk_preference": "高",
      "cached": false
    }
  ]
}
```

**使用场景**:
- 首次部署系统后，批量分析所有活跃交易者
- 定期刷新所有交易者的AI画像
- 分析新出现的活跃交易者

**注意事项**:
- 批量分析会调用AI API，消耗API额度
- 建议先小批量测试（10-20个）
- 已分析过的交易者会返回缓存结果（除非设置 force_refresh=true）

---

### 10. 内幕警报列表

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

### 11. 触发内幕分析

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

# 获取AI交易者排行榜
curl "http://localhost:8000/api/traders/ai-leaderboard?limit=20"

# 分析单个交易者
curl -X POST "http://localhost:8000/api/traders/0x1234.../ai-analyze?force_refresh=false"

# 批量AI分析
curl -X POST "http://localhost:8000/api/traders/batch-ai-analyze?limit=50&min_trades=5"

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

# 获取AI交易者排行榜
resp = requests.get("http://localhost:8000/api/traders/ai-leaderboard", params={"limit": 20})
ai_traders = resp.json()

# AI分析单个交易者
resp = requests.post("http://localhost:8000/api/traders/0x1234.../ai-analyze",
                     params={"force_refresh": False})
analysis = resp.json()

# 批量AI分析
resp = requests.post("http://localhost:8000/api/traders/batch-ai-analyze",
                     params={"limit": 50, "min_trades": 5})
batch_result = resp.json()
```

### JavaScript

```javascript
// 获取大单列表
const response = await fetch('http://localhost:8000/api/whales/live?limit=20');
const whales = await response.json();

// 获取AI交易者排行榜
const aiResponse = await fetch('http://localhost:8000/api/traders/ai-leaderboard?limit=20');
const aiTraders = await aiResponse.json();

// AI分析单个交易者
const analysisResponse = await fetch(
  'http://localhost:8000/api/traders/0x1234.../ai-analyze?force_refresh=false',
  { method: 'POST' }
);
const analysis = await analysisResponse.json();

// 批量AI分析
const batchResponse = await fetch(
  'http://localhost:8000/api/traders/batch-ai-analyze?limit=50&min_trades=5',
  { method: 'POST' }
);
const batchResult = await batchResponse.json();

// 触发内幕分析
const result = await fetch('http://localhost:8000/api/insider/analyze?limit=5', {
  method: 'POST'
});
```
