from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.users.models.dtos import UserProfileDTO

UserProfilesSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[UserProfileDTO]]
UserProfilesGetEnvelope: TypeAlias = SuccessEnvelope[dict]
UserProfilesCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserProfilesUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserProfilesDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

__all__ = [
    "UserProfilesSearchEnvelope",
    "UserProfilesGetEnvelope",
    "UserProfilesCreateEnvelope",
    "UserProfilesUpdateEnvelope",
    "UserProfilesDeleteEnvelope",
]
