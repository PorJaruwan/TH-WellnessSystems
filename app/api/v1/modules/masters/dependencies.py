from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

# This module is intentionally lightweight.
# Each router also provides its own small DI factory to keep imports local
# and reduce circular import risk.

def get_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    return session
