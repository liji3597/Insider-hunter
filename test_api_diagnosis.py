import asyncio
import os
import sys
from openai import AsyncOpenAI
from src.config import get_settings

# 强制使用 Windows 兼容的事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()

async def test_api():
    print(f"API Base: {settings.DEEPSEEK_BASE_URL}")
    print(f"API Key: {settings.DEEPSEEK_API_KEY[:8]}***")
    print(f"Model: {settings.DEEPSEEK_MODEL}")

    client = AsyncOpenAI(
        base_url=settings.DEEPSEEK_BASE_URL,
        api_key=settings.DEEPSEEK_API_KEY,
    )

    # Test 1: 基础连通性
    print("\n--- Test 1: 基础连通性 (Hello) ---")
    try:
        response = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=50
        )
        print("✅ 成功响应:", response.choices[0].message.content.strip())
    except Exception as e:
        print("❌ 失败:", str(e))

    # Test 2: 包含市场关键词
    print("\n--- Test 2: 市场关键词 (Bitcoin/Nvidia) ---")
    try:
        response = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": "Tell me a fact about Nvidia or Bitcoin."}],
            max_tokens=50
        )
        print("✅ 成功响应:", response.choices[0].message.content.strip())
    except Exception as e:
        print("❌ 失败:", str(e))

    # Test 3: 模拟实际 Prompt (无敏感词版)
    print("\n--- Test 3: 完整 Prompt 测试 ---")
    slug = "will-nvidia-be-the-largest-company-in-the-world-by-market-cap-on-january-31-985"
    topic = slug.replace("-", " ")

    prompt = f"""请查询以下主题在指定时间点的新闻动态：
主题: {topic}
关注时间点: 2024-01-31 12:00:00 UTC
任务要求：
1. 搜索该时间点前后 30 分钟内的相关公开报道
2. 确认新闻发布的具体时间
"""
    try:
        response = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个新闻调查助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        print("✅ 成功响应:", response.choices[0].message.content.strip()[:100] + "...")
    except Exception as e:
        print("❌ 失败:", str(e))

asyncio.run(test_api())
