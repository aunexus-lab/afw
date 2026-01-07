import asyncpg
from typing import Dict
from datetime import datetime
import json

class PostgresLogger:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=1, max_size=2)


    async def insert_event(self, event: Dict):
        query = """
        INSERT INTO log_events (
            timestamp, ip, port, process, user_name,
            action, success, source, parse_status,
            raw, parsed
        ) VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9,
            $10, $11
        )
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query,
                datetime.fromisoformat(event["timestamp"]) if isinstance(event["timestamp"], str) else event["timestamp"],
                event.get("ip"),
                event.get("port"),
                event.get("process"),
                event.get("user"),
                event.get("action"),
                event.get("success"),
                event.get("source"),
                event.get("parse_status"),
                event.get("raw"),
                json.dumps(event.get("parsed")) if event.get("parsed") else None
            )

    async def close(self):
        await self.pool.close()
