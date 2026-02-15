# app/db/base.py

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# ช่วยให้ Alembic autogenerate & constraint naming “เสถียร”
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    metadata = metadata_obj



# # note: ไว้เก็บ Declarative Base
# # app/db/base.py

# #from __future__ import annotations
# from sqlalchemy.orm import DeclarativeBase

# class Base(DeclarativeBase):
#     """
#     Base class สำหรับ SQLAlchemy ORM models ทั้งหมด
#     """
#     pass
