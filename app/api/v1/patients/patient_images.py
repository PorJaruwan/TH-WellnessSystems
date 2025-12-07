from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response, Query
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.patients_model import PatientImageCreateModel, PatientImageUpdateModel
from app.api.v1.services.patients_service import (
    create_patient_image, get_all_patient_images,
    get_patient_image_by_id, update_patient_image_by_id,
    delete_patient_image_by_id
)


router = APIRouter(
    prefix="/api/v1/patient_images",
    tags=["Patient_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_patient_image_by_id(patient_image: PatientImageCreateModel):
    try:
        data = jsonable_encoder(patient_image)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_patient_image(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient_image": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_patient_image_by_all():
    res = get_all_patient_images()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "patientImage": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_patient_image_by_id(patient_image_id: UUID):
    res = get_patient_image_by_id(patient_image_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_image_id": str(patient_image_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patientImage": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_patient_image_by_id(
    id: UUID = Query(..., description="ID of the patient image record to update"),
    patientImage: PatientImageUpdateModel = ...
):
    try:
        data = jsonable_encoder(patientImage)
        data.pop("patient_pic", None)  # Exclude from update
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = update_patient_image_by_id(id, cleaned_data)
        if not res.data:
            raise HTTPException(status_code=404, detail="Update failed or ID not found.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patientImage": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_patient_image_by_id(imageId: UUID):
    try:
        res = delete_patient_image_by_id(imageId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"imageId": str(imageId)})
        return ResponseHandler.success(
            message=f"patient image with imageId {imageId} deleted.",
            data={"imageId": str(imageId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
####JSON Request create test
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "patient_id": "683924c3-bbdb-498a-a7ac-533d4313c7dc",
  "patient_pic": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADUlEQVR42mP8Xw8AAoMBgZzByXQAAAAASUVORK5CYII=",
  "image_type": "JPEG",
  "description": "ทดสอบระบบ",
  "created_at": "2025-05-23T14:43:41.360Z",
  "updated_at": "2025-05-23T14:43:41.360Z"
}
"""