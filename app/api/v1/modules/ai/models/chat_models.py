# app/api/v1/modules/ai/models/chat_models.py

from __future__ import annotations

from sqlalchemy import Column, Text, Boolean, Integer, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.base import Base  # ใช้ base.py ของคุณ:contentReference[oaicite:6]{index=6}


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    company_code = Column(Text, nullable=False)

    app_context = Column(Text, nullable=False, server_default="patient")
    channel = Column(Text, nullable=True, server_default="flutterflow")

    user_id = Column(UUID(as_uuid=True), nullable=True)
    patient_id = Column(UUID(as_uuid=True), nullable=True)  # FK patients(id)
    staff_id = Column(UUID(as_uuid=True), nullable=True)    # FK staff(id)

    title = Column(Text, nullable=True)
    status = Column(Text, nullable=False, server_default="open")

    # ✅ FIX: reserved attribute "metadata" in SQLAlchemy Declarative
    meta = Column("metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    # V5 extension
    topic_code = Column(Text, nullable=True)
    triage_level = Column(Text, nullable=True)
    triage_reason = Column(Text, nullable=True)
    language = Column(Text, nullable=True, server_default="th-TH")
    last_activity_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    company_code = Column(Text, nullable=False)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    role = Column(Text, nullable=False)  # 'user','assistant','system','tool'
    content = Column(Text, nullable=False)

    content_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    model_provider = Column(Text, nullable=True)
    model_name = Column(Text, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
