
# app/database/database.py

from typing import AsyncGenerator
import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL

# ✅ ปิด prepared statement แบบชัวร์ (กันลืมที่ env)
# ✅ ensure asyncpg statement cache is disabled (safe for Supabase; also ok for direct)
if "statement_cache_size=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}statement_cache_size=0"

# ✅ Supabase uses SSL; keep it permissive for dev (as you had)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ✅ Direct DB (db.<ref>.supabase.co:5432) -> use pooled connections + recycle
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,     # ✅ กันค้างรอ connection
    pool_recycle=1800,   # 30 นาที
    pool_pre_ping=True,
    connect_args={
        "ssl": ssl_ctx,              # ✅ สำคัญ: ส่ง SSL context เข้าไปจริงๆ
        "statement_cache_size": 0,   # ✅ ปิด asyncpg statement cache
    },
)



# ✅ Pooler DB 
# # engine necnection for: pooler
# engine = create_async_engine(
#     DATABASE_URL,
#     poolclass=NullPool,          # ✅ ใช้ NullPool เมื่อผ่าน PgBouncer/Supabase pooler
#     pool_pre_ping=True,
#     connect_args={
#         "ssl": ssl_ctx,
#         "statement_cache_size": 0,          # ✅ ปิด statement cache ของ asyncpg
#         "prepared_statement_cache_size": 0, # ✅ (ถ้า dialect รองรับ) ปิดเพิ่มอีกชั้น
#     },
# )


# engine = create_async_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     pool_size=5,
#     max_overflow=10,
#     connect_args={
#         "ssl": ssl_ctx,
#         "statement_cache_size": 0,
#         "prepared_statement_cache_size": 0,
#     },
# )

###ตัวเดิม
# engine = create_async_engine(
#     DATABASE_URL,            # ✅ ใช้ตัวที่เติม statement_cache_size=0 แล้ว
#     poolclass=NullPool,
#     pool_pre_ping=True,
#     connect_args={
#         "ssl": ssl_ctx,
#         "statement_cache_size": 0,
#     },
#     echo=False,
# )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal() as session:
#         yield session
