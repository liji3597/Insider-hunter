import asyncio
from sqlalchemy import text
from src.db import AsyncSessionLocal, init_db

async def clear():
    await init_db()
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE insider_alerts RESTART IDENTITY"))
        await session.commit()
        print("OK: insider_alerts cleared")

asyncio.run(clear())
