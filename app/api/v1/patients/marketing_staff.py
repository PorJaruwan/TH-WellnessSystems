from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import MarketingStaffCreate, MarketingStaffUpdate
from app.api.v1.services.patients_service import (
    create_marketing_staff,
    get_all_marketing_staff,
    get_marketing_staff_by_id,
    update_marketing_staff_by_id,
    delete_marketing_staff_by_id,
)

router = APIRouter(
    prefix="/api/v1/marketing_staff",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_marketing_staff_by_id(
    marketingStaff: MarketingStaffCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await create_marketing_staff(db, marketingStaff)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"marketingStaff": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_marketing_staff_by_all(
    db: AsyncSession = Depends(get_db),
):
    items = await get_all_marketing_staff(db)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(items), "marketingStaff": items},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_marketing_staff_by_id(
    marketing_staff_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_marketing_staff_by_id(db, marketing_staff_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"marketing_staff_id": str(marketing_staff_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"marketingStaff": item},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_marketing_staff(
    marketing_staff_id: UUID,
    marketingStaff: MarketingStaffUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await update_marketing_staff_by_id(db, marketing_staff_id, marketingStaff)
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"marketing_staff_id": str(marketing_staff_id)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"marketingStaff": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_marketing_staff(
    marketing_staff_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_marketing_staff_by_id(db, marketing_staff_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"marketing_staff_id": str(marketing_staff_id)},
            )
        return ResponseHandler.success(
            message=f"Marketing Staff with ID {marketing_staff_id} deleted.",
            data={"marketing_staff_id": str(marketing_staff_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
