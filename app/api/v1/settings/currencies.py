from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder

from app.api.v1.models.settings_model import CurrencyCreate, CurrencyUpdate
from app.api.v1.services.settings_service import (
    create_currency, get_all_currencies, get_currency_by_code,
    update_currency_by_code, delete_currency_by_code
)

router = APIRouter(
    prefix="/api/v1/currencies",
    tags=["Core_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_currency_by_code(currencies: CurrencyCreate):
    try:
        data = jsonable_encoder(currencies)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_currency(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"currencies": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
def read_currency_by_all():
    res = get_all_currencies()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "currencies": res.data}
    )

@router.get("/search-by-code", response_class=UnicodeJSONResponse)
def read_currency_by_code(currency_code: str):
    res = get_currency_by_code(currency_code)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"currency_code": str(currency_code)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"currencies": res.data[0]}
    )

@router.put("/update-by-code", response_class=UnicodeJSONResponse)
def update_currency(currencyCode: str, currencies: CurrencyUpdate):
    try:
        updated = {
            "currency_name": currencies.currency_name,
            "symbol": currencies.symbol,
            "decimal_places": currencies.decimal_places,
        }
        res = update_currency_by_code(currencyCode, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"currencyCode": str(currencyCode)})

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"currencies": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-code", response_class=UnicodeJSONResponse)
def delete_currency(currencyCode: str):
    try:
        res = delete_currency_by_code(currencyCode)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"currencyCode": str(currencyCode)})
        return ResponseHandler.success(
            message=f"addresses with currency code {currencyCode} deleted.",
            data={"currencyCode": str(currencyCode)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
