from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder

from app.api.v1.models.settings_model import LanguagesCreateModel, LanguagesUpdateModel
from app.api.v1.services.settings_service import (
    create_language, get_all_languages, get_language_by_code,
    update_language_by_code, delete_language_by_code
)

router = APIRouter(
    prefix="/api/v1/languages",
    tags=["Core_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_language_by_code(languages: LanguagesCreateModel):
    try:
        data = jsonable_encoder(languages)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_language(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"languages": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_class=UnicodeJSONResponse)
def read_language_by_all():
    res = get_all_languages()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "languages": res.data}
    )

@router.get("/search-by-code", response_class=UnicodeJSONResponse)
def read_language(language_code: str):
    res = get_language_by_code(language_code)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"language_code": str(language_code)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"languages": res.data[0]}
    )

@router.put("/update-by-code", response_class=UnicodeJSONResponse)
def update_language_by_id(languageCode: str, languages: LanguagesUpdateModel):
    try:
        updated = {
            "language_name": languages.language_name,
        }
        res = update_language_by_code(languageCode, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"languageCode": str(languageCode)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"languages": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-code", response_class=UnicodeJSONResponse)
def delete_language_by_id(languageCode: str):
    try:
        res = delete_language_by_code(languageCode)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"languageCode": str(languageCode)})
        return ResponseHandler.success(
            message=f"addresses with languageCode {languageCode} deleted.",
            data={"languageCode": str(languageCode)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
