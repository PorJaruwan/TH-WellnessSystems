from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.core.config import get_settings
settings = get_settings()

#engine = create_async_engine(settings.DATABASE_URL, echo=False)
engine = create_async_engine(settings.DATABASE_URL,echo=False,future=True,)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionLocal = async_sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession,)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# app/core/db.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency สำหรับ FastAPI
    ใช้แบบ: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


#####Old
# import os
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from fastapi import Depends
# from typing import AsyncGenerator
# from dotenv import load_dotenv

# load_dotenv()

# # ✅ แก้ตรงนี้: ใช้ DATABASE_URL ที่ได้จาก Supabase
# DATABASE_URL = os.getenv("DATABASE_URL")  # ต้องตั้งไว้ใน .env

# # ✅ สร้าง engine ด้วย URL แบบ string
# engine = create_async_engine(DATABASE_URL, echo=False)
# async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session() as session:
#         yield session


