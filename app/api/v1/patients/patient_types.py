from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.patients_model import PatientTypeCreateModel, PatientTypeUpdateModel
from app.api.v1.services.patients_service import (
    create_patient_type, get_all_patient_types, get_patient_type_by_id,
    update_patient_type_by_id, delete_patient_type_by_id
)

router = APIRouter(
    prefix="/api/v1/patient_types",
    tags=["Patient_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_patient_type_by_id(patientType: PatientTypeCreateModel):
    try:
        data = jsonable_encoder(patientType)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_patient_type(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patientType": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_patient_type_by_all():
    res = get_all_patient_types()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "patientType": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_patient_type_by_id(patient_type_id: UUID):
    res = get_patient_type_by_id(patient_type_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_type_id": str(patient_type_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patientType": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_patient_type_by_id(patient_type_id: UUID, patientType: PatientTypeUpdateModel):
    updated = {
        "type_name": patientType.type_name,
        "description": patientType.description,
    }
    res = update_patient_type_by_id(patient_type_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_type_id": str(patient_type_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"patientType": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_patient_type_by_id(patient_type_id: UUID):
    try:
        res = delete_patient_type_by_id(patient_type_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_type_id": str(patient_type_id)})
        return ResponseHandler.success(
            message=f"Patient type with ID {patient_type_id} deleted.",
            data={"patient_type_id": str(patient_type_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
