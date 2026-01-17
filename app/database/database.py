# app/database/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
import ssl
import certifi

settings = get_settings()

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


###เช็คว่า engine ใช้ settings.DATABASE_URL จริง
# engine = create_async_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,
#     connect_args={"ssl": True},
# )

###ใช้ certifi แล้วส่ง ssl context ให้ asyncpg และติดตั้ง certifi (ถ้ายังไม่มี)
# engine = create_async_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,
#     connect_args={
#         "ssl": ssl.create_default_context(cafile=certifi.where())
#     },
# )

#ใช้ทางเลือก A (แนะนำสำหรับ Render/Pooler): ใช้ SSL “require แต่ไม่ verify”
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_ctx},
)

#ทางเลือก B (ดีที่สุดด้าน security): ใช้ Host/Mode ที่ Supabase แนะนำให้ verify ผ่าน
#เปลี่ยน connection string ใน Supabase เป็น Session pooler จริง ๆ และใช้ host ที่ตรงตาม region/pooler ที่ Supabase ให้มา (บางครั้งคนเผลอใช้ Transaction pooler หรือ copy ผิดช่อง)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
