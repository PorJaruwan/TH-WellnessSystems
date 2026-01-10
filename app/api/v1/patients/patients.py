from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from urllib.parse import unquote
from uuid import UUID

from app.api.v1.models.patients_model import PatientsCreateModel, PatientsUpdateModel
from app.api.v1.services.patients_service import (
    get_all_patients,
    get_patient_by_id,
    get_patient_by_name,
    #get_patient_by_code,
    create_patient,
    update_patient,
    delete_patient
)

router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patient_Settings"]
)

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_patient_by_all():
    try:
        data = get_all_patients()
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"total": len(data), "patients": data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ READ BY patient_id
@router.get("/search-by-patient-id", response_class=UnicodeJSONResponse)
def read_patient_by_id(patient_id: UUID):
    res = get_patient_by_id(patient_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patient": res.data[0]}
    )


# @router.get("/search-by-code", response_class=UnicodeJSONResponse)
# def read_patient_by_code(patient_code: str):
#     try:
#         data = get_patient_by_code(patient_code)
#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data=data
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_patient_by_name(request: Request, find_name: str = "", status: str = ""):
    try:
        decoded_find_name = unquote(find_name)
        patients = get_patient_by_name(decoded_find_name, status)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"total": len(patients), "patients": patients}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_patient_by_id(patient: PatientsCreateModel):
    try:
        created = create_patient(patient)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient": created}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ UPDATE patient BY ID
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_patient_by_id(patient_id: str, patients: PatientsUpdateModel):
    try:
        updated = update_patient(patient_id, patients)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patients": updated}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_patient_by_id(patient_id: str):
    try:
        deleted = delete_patient(patient_id)
        return ResponseHandler.success(
            message=f"Patient with Patient ID {patient_id} deleted.",
            data={"patient_id": deleted}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


