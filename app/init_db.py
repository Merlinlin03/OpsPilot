"""Create missing application tables without removing existing records."""
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.config.config import settings
from app.repository.base import Base
from app.repository.dialogue_state import DialogueStateRecord  # Register the table.


async def main():
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
