# note: ไว้เก็บ Declarative Base
# app/db/base.py

#from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class สำหรับ SQLAlchemy ORM models ทั้งหมด
    """
    pass
