# # app/utils/payload_cleaner.py
from __future__ import annotations
from typing import Any, Dict, Iterable, Optional

AUDIT_FIELDS_DEFAULT = {"created_at", "updated_at"}


def clean_payload_dict(
    data: Dict[str, Any],
    *,
    drop_audit_fields: bool = True,
    extra_drop_fields: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    - ""  -> None
    - drop created_at / updated_at (default)
    """
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}

    drop_fields = set(extra_drop_fields or [])
    if drop_audit_fields:
        drop_fields |= AUDIT_FIELDS_DEFAULT

    return {k: v for k, v in cleaned.items() if k not in drop_fields}


def clean_create(model, **kwargs) -> Dict[str, Any]:
    """ใช้กับ POST /create"""
    return clean_payload_dict(model.model_dump(), **kwargs)


def clean_update(model, **kwargs) -> Dict[str, Any]:
    """ใช้กับ PUT /update"""
    return clean_payload_dict(model.model_dump(exclude_unset=True), **kwargs)


