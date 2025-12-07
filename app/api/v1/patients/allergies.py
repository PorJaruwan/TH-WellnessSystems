from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.patients_model import AllergyCreateModel, AllergyUpdateModel
from app.api.v1.services.patients_service import (
    create_allergy, get_all_allergies, get_allergy_by_id,
    update_allergy_by_id, delete_allergy_by_id
)


router = APIRouter(
    prefix="/api/v1/allergies",
    tags=["Patient_Settings"]
)


@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_allergy_by_id(allergy: AllergyCreateModel):
    try:
        data = jsonable_encoder(allergy)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_allergy(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"allergy": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_allergy_by_all():
    res = get_all_allergies()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "allergy": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_allergy_by_id(allergy_id: UUID):
    res = get_allergy_by_id(allergy_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"allergy": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_allergy(allergy_id: UUID, allergy: AllergyUpdateModel):
    updated_data = {
        "allergy_name": allergy.allergy_name,
        "description": allergy.description
    }
    res = update_allergy_by_id(allergy_id, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"allergy": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_allergy(allergy_id: UUID):
    try:
        res = delete_allergy_by_id(allergy_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
        return ResponseHandler.success(
            message=f"Allergy with id {allergy_id} deleted.",
            data={"allergy_id": str(allergy_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
