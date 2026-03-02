from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from pydantic import BaseModel
from uuid import UUID

# logging
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.user_access")


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/check_access",
    tags=["User_Authen"],
)

class CheckAccessRequest(BaseModel):
    profile_id: UUID
    route: str
    method: str
    company_code: str

class CheckAccessResponse(BaseModel):
    has_access: bool

@router.post("/check", response_class=UnicodeJSONResponse, summary="ตรวจสอบสิทธิ์ผู้ใช้", response_description="ผลลัพธ์การตรวจสอบสิทธิ์ผู้ใช้งาน")
async def check_access(data: CheckAccessRequest):
    try:
        logger.info("📥 Received check_access request: profile_id=%s, route=%s, method=%s, company_code=%s",
                    data.profile_id, data.route, data.method, data.company_code)

        response = supabase.rpc("check_access", {
            "p_profile_id": str(data.profile_id),
            "p_route": data.route,
            "p_method": data.method,
            "p_company_code": data.company_code
        }).execute()

        logger.info("✅ Supabase RPC response: data=%s", response.data)

        # ✅ ตรวจว่าผลลัพธ์เป็น boolean หรือไม่
        if isinstance(response.data, bool):
            return ResponseHandler.success(
                message="Access checked successfully",
                data={"has_access": response.data}
            )
        else:
            logger.error("❗ Unexpected RPC result format: %s", response.data)
            return ResponseHandler.error(
                code="RPC_002",
                message="Unexpected RPC result format",
                details={"raw_result": response.data},
                status_code=500
            )

    except Exception as e:
        logger.exception("🔥 Exception occurred in check_access: %s", str(e))
        return ResponseHandler.error(
            code="SYS_001",
            message="Exception occurred while checking access",
            details={"error": str(e)},
            status_code=500
        )
