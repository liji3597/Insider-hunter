"""Simplified AI Trader Profile Test Script"""
import asyncio
import sys

# Step 1: Check dependencies
print("=== Step 1: Check Dependencies ===")
try:
    import openai
    print("[OK] openai installed")
except ImportError:
    print("[FAIL] openai not installed, run: pip install openai")
    sys.exit(1)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    print("[OK] sqlalchemy installed")
except ImportError:
    print("[FAIL] sqlalchemy not installed, run: pip install sqlalchemy[asyncio]")
    sys.exit(1)

try:
    from src.config import get_settings
    print("[OK] Project config loaded")
    settings = get_settings()
    print(f"  API Base: {settings.DEEPSEEK_BASE_URL}")
    print(f"  Model: {settings.DEEPSEEK_MODEL}")
    print(f"  API Key: {settings.DEEPSEEK_API_KEY[:20]}...")
except Exception as e:
    print(f"[FAIL] Config load failed: {e}")
    sys.exit(1)

# Step 2: Check database connection
print("\n=== Step 2: Check Database Connection ===")
try:
    from src.db import init_db, close_db, AsyncSessionLocal

    async def test_db():
        await init_db()
        print("[OK] Database connected")

        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM trader_profiles"))
            count = result.scalar()
            print(f"[OK] trader_profiles table has {count} records")

        await close_db()

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(test_db())

except Exception as e:
    print(f"[FAIL] Database connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test AI module import
print("\n=== Step 3: Test AI Module ===")
try:
    from src.profiler.ai_analyzer import TraderAIProfiler
    print("[OK] TraderAIProfiler module imported")
except Exception as e:
    print(f"[FAIL] AI module import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[SUCCESS] All basic checks passed!")
print("="*60)
print("\nNext steps:")
print("1. Run database migration:")
print("   docker exec insider-hunter-db psql -U hunter -d polymarket_db")
print("   Then: ALTER TABLE trader_profiles ADD COLUMN IF NOT EXISTS trading_style VARCHAR(50), ADD COLUMN IF NOT EXISTS risk_preference VARCHAR(20), ADD COLUMN IF NOT EXISTS ai_analysis TEXT;")
print("\n2. Run AI analysis: py -m src.main ai-profile 5")
