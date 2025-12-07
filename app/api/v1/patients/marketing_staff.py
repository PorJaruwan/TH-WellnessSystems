from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import MarketingStaffCreateModel, MarketingStaffUpdateModel
from app.api.v1.services.patients_service import (
    create_marketing_staff, get_all_marketing_staff, get_marketing_staff_by_id,
    update_marketing_staff_by_id, delete_marketing_staff_by_id
)

router = APIRouter(
    prefix="/api/v1/marketing_staff",
    tags=["Patient_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_marketing_staff_by_id(marketingStaff: MarketingStaffCreateModel):
    try:
        data = jsonable_encoder(marketingStaff)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_marketing_staff(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"marketingStaff": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_marketing_staff_by_all():
    res = get_all_marketing_staff()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "marketingStaff": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_marketing_staff_by_id(marketing_staff_id: UUID):
    res = get_marketing_staff_by_id(marketing_staff_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"marketing_staff_id": str(marketing_staff_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"marketingStaff": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_marketing_staff(marketing_staff_id: UUID, marketingStaff: MarketingStaffUpdateModel):
    updated = {
        "marketing_name": marketingStaff.marketing_name,
        "campaign": marketingStaff.campaign,
    }
    res = update_marketing_staff_by_id(marketing_staff_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"marketing_staff_id": str(marketing_staff_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"marketing_staff_id": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_marketing_staff(marketing_staff_id: UUID):
    try:
        res = delete_marketing_staff_by_id(marketing_staff_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"marketing_staff_id": str(marketing_staff_id)})
        return ResponseHandler.success(
            message=f"Marketing Staff with ID {marketing_staff_id} deleted.",
            data={"marketing_staff_id": str(marketing_staff_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
