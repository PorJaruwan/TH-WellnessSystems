
# app/database/database.py (Version: ...)
from typing import AsyncGenerator
import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL

# ✅ ปิด prepared statement แบบชัวร์ (กันลืมที่ env)
if "statement_cache_size=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}statement_cache_size=0"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,            # ✅ ใช้ตัวที่เติม statement_cache_size=0 แล้ว
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args={
        "ssl": ssl_ctx,
        "statement_cache_size": 0,
    },
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session




# # app/database/database.py (Version: patient ORM refectory compleate)
# from typing import AsyncGenerator
# import ssl

# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from sqlalchemy.pool import NullPool

# from app.core.config import get_settings

# settings = get_settings()

# ssl_ctx = ssl.create_default_context()
# ssl_ctx.check_hostname = False
# ssl_ctx.verify_mode = ssl.CERT_NONE

# engine = create_async_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,

#     # ✅ สำคัญ: กัน DuplicatePreparedStatementError บน Pooler
#     connect_args={
#         "ssl": ssl_ctx,
#         "statement_cache_size": 0,
#     },

#     # ✅ แนะนำเมื่อใช้ Pooler อยู่แล้ว (กัน SQLAlchemy pool ซ้อน)
#     poolclass=NullPool,
# )

# AsyncSessionLocal = async_sessionmaker(
#     bind=engine,
#     expire_on_commit=False,
#     class_=AsyncSession,
# )

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal() as session:
#         yield session
