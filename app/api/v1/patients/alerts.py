from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from datetime import datetime

from app.api.v1.models.patients_model import AlertCreateModel, AlertUpdateModel
from app.api.v1.services.patients_service import (
    create_alert, get_all_alerts, get_alert_by_id,
    update_alert_by_id, delete_alert_by_id
)

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Patient_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_alert_by_id(alert: AlertCreateModel):
    try:
        data = jsonable_encoder(alert)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_alert(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"alert": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_alert_by_all():
    res = get_all_alerts()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "alerts": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_alert_by_id(alert_id: UUID):
    res = get_alert_by_id(alert_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"alerts": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_alert(alert_id: UUID, alert: AlertUpdateModel):
    updated_data = {
        "alert_type": alert.alert_type,
        "description": alert.description,
        "created_at": datetime.utcnow().isoformat()
    }
    res = update_alert_by_id(alert_id, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"alerts": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_alert(alert_id: UUID):
    try:
        res = delete_alert_by_id(alert_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
        return ResponseHandler.success(
            message=f"Alert with id {alert_id} deleted.",
            data={"alert_id": str(alert_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
