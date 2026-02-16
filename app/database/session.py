# app/database/session.py

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

# NOTE: AsyncSessionLocal is configured with expire_on_commit=False in app/database/database.py
from app.database.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
