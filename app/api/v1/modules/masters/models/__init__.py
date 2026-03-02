# app/api/v1/modules/masters/models/__init__.py
from __future__ import annotations

"""
masters.models package

Rule:
- Do NOT import *_envelopes modules directly here (avoid wrong paths & circular imports).
- If someone needs envelopes, import from:
  app.api.v1.modules.masters.models._envelopes
- If someone needs DTOs/response models, import from:
  app.api.v1.modules.masters.models.dtos / settings_response_model
"""

from .dtos import *  # noqa: F401,F403

__all__ = []
__all__ += list(globals().keys())