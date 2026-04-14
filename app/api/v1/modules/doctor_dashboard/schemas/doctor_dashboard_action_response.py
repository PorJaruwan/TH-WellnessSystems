from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DoctorDashboardActionResultData(BaseModel):
    booking_id: str
    status: Optional[str] = None
    note_status: Optional[str] = None
    message_detail: Optional[str] = None


class DoctorDashboardActionResponse(BaseModel):
    status: str = "success"
    status_code: int = 200
    message: str = "Doctor dashboard action completed successfully."
    data: DoctorDashboardActionResultData
    timestamp: datetime = Field(default_factory=datetime.utcnow)