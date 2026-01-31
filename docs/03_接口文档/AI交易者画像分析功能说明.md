# AI 交易者画像分析功能说明

## 功能概述

基于 DeepSeek V3 的 AI 深度分析模块，自动分析交易者的行为特征、交易风格和决策模式，生成专业的交易者画像评价。

## 核心特性

### 1. 多维度分析
- **交易风格**：激进/稳健/保守/投机/对冲
- **风险偏好**：高风险/中等/低风险
- **决策特点**：理性/情绪化/数据驱动/跟风
- **擅长领域**：政治/体育/娱乐等
- **行为特征**：长期持有/短线交易/对冲等

### 2. AI 生成内容
- **个性化标签**：如"激进型政治预测专家"、"稳健长线价值投资者"
- **深度分析报告**：150-300字专业评价，包含核心特征、决策特点、优势与风险
- **行为洞察**：基于历史交易记录的模式识别

### 3. 智能缓存
- 已分析过的交易者自动缓存结果
- 支持强制刷新模式（`--force`）
- 避免重复 API 调用，节省成本

## 数据库字段

在 `trader_profiles` 表中新增以下字段：

```sql
-- AI 分析字段
label           VARCHAR(100)  -- AI 生成的标签
trading_style   VARCHAR(50)   -- 交易风格
risk_preference VARCHAR(20)   -- 风险偏好
ai_analysis     TEXT          -- AI 深度分析文本
```

## 使用方法

### 1. 数据库迁移

首先运行数据库迁移脚本添加新字段：

```bash
# 方式一：使用 psql 命令
psql -h localhost -U hunter -d polymarket_db -f migrations/add_ai_profile_fields.sql

# 方式二：手动连接数据库执行
docker exec -it polymarket-db psql -U hunter -d polymarket_db
\i /path/to/migrations/add_ai_profile_fields.sql
```

### 2. 命令行分析

```bash
# 基础用法：分析前 50 个交易者（最少 5 笔交易）
python -m src.main ai-profile

# 自定义数量：分析前 100 个交易者
python -m src.main ai-profile 100

# 自定义筛选条件：分析前 30 个交易者（最少 10 笔交易）
python -m src.main ai-profile 30 10

# 强制刷新：重新分析已有标签的交易者
python -m src.main ai-profile 50 5 --force

# Windows 平台建议加上策略修复
python -m src.main ai-profile
```

### 3. API 接口调用

#### 3.1 获取 AI 排行榜

```bash
# 获取带 AI 分析的交易者排行榜
curl http://localhost:8000/api/traders/ai-leaderboard?limit=20

# 筛选聪明钱
curl http://localhost:8000/api/traders/ai-leaderboard?trader_type=smart_money
```

响应示例：
```json
{
  "data": [
    {
      "address": "0x1234...",
      "label": "激进型政治预测专家",
      "trader_type": "smart_money",
      "trading_style": "激进",
      "risk_preference": "高",
      "ai_analysis": "该交易者展现出明显的激进风格...",
      "win_rate": 92.5,
      "total_trades": 45,
      "total_volume": 125000.00,
      "avg_trade_size": 2777.78,
      "last_trade_at": "2024-01-30T10:00:00"
    }
  ]
}
```

#### 3.2 分析单个交易者

```bash
# 分析指定地址
curl -X POST "http://localhost:8000/api/traders/0x1234.../ai-analyze"

# 强制重新分析
curl -X POST "http://localhost:8000/api/traders/0x1234.../ai-analyze?force_refresh=true"
```

#### 3.3 批量分析

```bash
# 批量分析 100 个交易者
curl -X POST "http://localhost:8000/api/traders/batch-ai-analyze?limit=100&min_trades=5"
```

## 工作流程

### 推荐使用流程

1. **数据准备**（首次使用）
   ```bash
   # 1. 同步市场数据
   python -m src.main sync-markets

   # 2. 快速回填交易数据
   python -m src.main fast-backfill 10000

   # 3. 刷新交易者画像（基础统计）
   python -m src.main refresh-profiles
   ```

2. **AI 分析**
   ```bash
   # 4. 运行 AI 画像分析
   python -m src.main ai-profile 100 10
   ```

3. **查看结果**
   ```bash
   # 5. 启动 API 服务查看结果
   python -m src.main serve
   # 访问 http://localhost:8000/api/traders/ai-leaderboard
   ```

### 定期更新流程

```bash
# 每日更新脚本示例
# 1. 刷新基础画像
python -m src.main refresh-profiles

# 2. 分析新交易者（跳过已分析的）
python -m src.main ai-profile 50 5

# 3. 定期全量刷新（每周一次）
python -m src.main ai-profile 200 5 --force
```

## AI 分析示例

### 输入数据
```
交易者地址: 0xabcd1234...
总交易次数: 48
总交易量: $156,000
胜率: 89.5% (34胜 / 4败)
平均单笔: $3,250
买卖比例: 40:8
大单次数: 12
```

### AI 输出示例
```json
{
  "label": "稳健型政治预测专家",
  "trading_style": "稳健",
  "risk_preference": "中",
  "analysis": "该交易者展现出稳健的投资风格，以中等规模的交易量参与政治预测市场。其89.5%的胜率显示出较强的判断能力和信息优势。交易行为特征显示其倾向于做多（买入YES），且能够准确把握政治事件的走向。12次大额交易表明在高确定性机会出现时会加大投注，体现了理性的风险管理。整体来看，这是一位经验丰富、决策谨慎的专业预测者，擅长政治类市场，具有较高的可信度。建议关注其大额交易信号。"
}
```

## 注意事项

### 成本优化
- AI 分析会调用 DeepSeek API，建议：
  - 先分析小批量测试（10-20个）
  - 使用缓存机制，避免重复分析
  - 仅对活跃交易者进行分析（min_trades >= 5）

### 性能建议
- 批量分析时建议每次不超过 200 个
- API 调用有速率限制，注意控制并发
- 大批量分析建议在后台运行

### 数据质量
- 确保已运行 `refresh-profiles` 刷新基础统计
- 已结算市场越多，胜率统计越准确
- 新用户（交易次数少）的分析可能不够准确

## 故障排查

### 常见问题

1. **"未找到交易者画像"**
   ```bash
   # 解决：先刷新基础画像
   python -m src.main refresh-profiles
   ```

2. **"AI 分析调用失败"**
   - 检查 `.env` 文件中的 API Key 配置
   - 确认 API 余额充足
   - 检查网络连接

3. **分析结果为空**
   - 确认交易者有足够的历史交易
   - 检查数据库中是否有已结算市场
   - 查看控制台输出的详细日志

### 调试模式

```python
# 手动测试单个交易者分析
import asyncio
from src.db import init_db, AsyncSessionLocal
from src.profiler.ai_analyzer import TraderAIProfiler

async def test():
    await init_db()
    ai_profiler = TraderAIProfiler(AsyncSessionLocal)

    async with AsyncSessionLocal() as session:
        result = await ai_profiler.analyze_trader(
            session=session,
            address="0x你的地址",
            force_refresh=True
        )
        print(result)

asyncio.run(test())
```

## API 文档

完整的 API 文档可访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技术架构

```
┌─────────────────────────────────────┐
│   trader_profiles (基础统计)         │
│   - 胜率、交易量、交易次数等         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   TraderAIProfiler                  │
│   - 准备分析数据                     │
│   - 构建 AI Prompt                  │
│   - 调用 DeepSeek V3                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   DeepSeek V3 API                   │
│   - 深度分析交易行为                 │
│   - 生成标签和评价                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   更新数据库                         │
│   - label, trading_style            │
│   - risk_preference, ai_analysis    │
└─────────────────────────────────────┘
```

## 未来扩展

- [ ] 支持自定义分析维度
- [ ] 添加交易者对比功能
- [ ] 生成 PDF 报告
- [ ] 实时监控高价值交易者
- [ ] 集成社交媒体分析
