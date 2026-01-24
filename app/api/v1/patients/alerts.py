from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import AlertCreate, AlertUpdate
from app.api.v1.services.patients_service import (
    create_alert,
    get_all_alerts,
    get_alert_by_id,
    update_alert_by_id,
    delete_alert_by_id,
)

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_alert_by_id(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new alert (async ORM)."""
    try:
        obj = await create_alert(db, alert)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"alert": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_alert_by_all(
    db: AsyncSession = Depends(get_db),
):
    alerts = await get_all_alerts(db)
    if not alerts:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(alerts), "alerts": alerts},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_alert_by_id(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    alert = await get_alert_by_id(db, alert_id)
    if alert is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"alert_id": str(alert_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"alert": alert},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_alert(
    alert_id: UUID,
    alert: AlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing alert by ID."""
    try:
        obj = await update_alert_by_id(db, alert_id, alert)
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"alert_id": str(alert_id)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"alert": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete alert by ID."""
    try:
        deleted = await delete_alert_by_id(db, alert_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"alert_id": str(alert_id)},
            )
        return ResponseHandler.success(
            message=f"Alert with id {alert_id} deleted.",
            data={"alert_id": str(alert_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



