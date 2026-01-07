import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from core.parser.auth import parse_with_status
from core.ingest.tail_log import replay_log
from core.storage.postgres import PostgresLogger

load_dotenv()

LOG_PATH = Path("tests/fixtures/ingest/samples/auth.log")
PG_DSN = os.getenv("PG_DSN")

async def main():
    logger = PostgresLogger(PG_DSN)
    await logger.connect()

    for line in replay_log(LOG_PATH):
        event = parse_with_status(line)
        print(f"✅ Inserted: {event['timestamp']} - {event['action']}")
        await logger.insert_event(event)

    await logger.close()

if __name__ == "__main__":
    asyncio.run(main())
