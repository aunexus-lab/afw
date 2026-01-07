import asyncio
import os
from dotenv import load_dotenv
import asyncpg
import pytest

load_dotenv()

DSN = os.getenv("PG_DSN")

@pytest.mark.asyncio
async def test_connection():
    try:
        print("🔌 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(dsn=DSN)
        version = await conn.fetchval("SELECT version();")
        print("✅ Connected!")
        print(f"📦 PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    asyncio.run(test_connection())
