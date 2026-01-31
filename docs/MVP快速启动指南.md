# Insider Hunter MVP 快速启动指南

> 本指南帮助新手在 Windows 上一步步运行项目

---

## 第一步：检查前置条件

### 1.1 确认 Python 已安装
打开 PowerShell 或 CMD，运行：
```bash
py --version
```
应该看到 `Python 3.9.x` 或更高版本。

### 1.2 确认 Docker Desktop 已安装
如果没有安装，请从这里下载：https://www.docker.com/products/docker-desktop/

安装后确认：
```bash
docker --version
docker-compose --version
```

---

## 第二步：配置环境变量

### 2.1 创建 .env 文件
在项目根目录（`D:\RustProject\insider-hunter`）创建 `.env` 文件：

```bash
cd D:\RustProject\insider-hunter
copy .env.example .env
```

### 2.2 编辑 .env 文件
用记事本或 VS Code 打开 `.env`，填入以下内容：

```ini
# 数据库配置（保持默认即可）
DATABASE_URL=postgresql+asyncpg://hunter:hunter123@localhost:5432/polymarket_db

# Polygon RPC（必须填写，下面是免费公共 RPC）
POLYGON_RPC_URL=https://polygon-rpc.com

# DeepSeek API（必须填写你的 API Key）
DEEPSEEK_BASE_URL=https://key.jese1357.xyz/v1
DEEPSEEK_API_KEY=sk-lb-8f4e2a9c7b1d6e3f5a0c9d8b7e6f4a2c
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3

# 业务配置
WHALE_THRESHOLD=10000
```

**重要**：把 `你的API密钥` 替换成真实的 DeepSeek API Key！

---

## 第三步：启动数据库

### 3.1 启动 Docker Desktop
双击桌面的 Docker Desktop 图标，等待它完全启动（托盘图标变绿）。

### 3.2 启动 PostgreSQL
打开 PowerShell，运行：
```bash
cd D:\RustProject\insider-hunter
docker-compose up -d
```

### 3.3 验证数据库运行
```bash
docker ps
```
应该看到 `insider-hunter-db` 容器正在运行。

---

## 第四步：启动 API 服务

### 4.1 运行服务
```bash
cd D:\RustProject\insider-hunter
py -m src.main serve
```

### 4.2 预期输出
```
🚀 Insider Hunter 启动中...
✓ 数据库初始化完成
✓ 同步了 50 个新市场，共 150 个活跃市场
✓ 链上监听器已启动
✓ Insider Hunter 启动完成!
  API 地址: http://localhost:8000
  文档地址: http://localhost:8000/docs
```

### 4.3 测试 API
打开浏览器，访问：
- http://localhost:8000 - 首页
- 
 - Swagger API 文档

---

## 第五步：验证功能

### 5.1 测试健康检查
打开新的 PowerShell 窗口：
```bash
curl http://localhost:8000/api/health
```
或在浏览器访问该地址。

### 5.2 查看市场列表
```bash
curl http://localhost:8000/api/markets?limit=5
```

### 5.3 查看大单列表
```bash
curl http://localhost:8000/api/whales/live?limit=10
```

---

## 第六步：回填历史数据（可选）

如果想获取历史数据，在新窗口运行：
```bash
cd D:\RustProject\insider-hunter
py -m src.main backfill 1
```
这会回填最近 1 个月的数据（约需 30 分钟）。

---

## 常见问题

### Q: 启动时报 "connection refused" 错误
A: 数据库没启动。运行 `docker-compose up -d` 后等待 10 秒再试。

### Q: 中文乱码
A: Windows 控制台编码问题，不影响功能。

### Q: 没有看到大单数据
A: 需要等待链上有新的大单交易，或先回填历史数据。

### Q: API Key 无效
A: 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确。

---

## 停止服务

### 停止 API
在运行 API 的窗口按 `Ctrl + C`

### 停止数据库
```bash
cd D:\RustProject\insider-hunter
docker-compose down
```

---

## 项目文件说明

```
insider-hunter/
├── .env                 # 你的配置文件（包含密钥，不要上传到 Git）
├── .env.example         # 配置模板
├── docker-compose.yml   # 数据库配置
├── requirements.txt     # Python 依赖
├── src/                 # 源代码
│   ├── main.py          # 程序入口
│   ├── api/             # API 接口
│   ├── indexer/         # 链上数据抓取
│   ├── profiler/        # 交易者画像
│   └── agent/           # AI 分析
└── docs/                # 文档
```
