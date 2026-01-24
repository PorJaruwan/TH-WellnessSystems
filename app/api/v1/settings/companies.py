# app/api/v1/settings/companies.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.payload_cleaner import clean_create, clean_update  # ✅ DRY
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.database.session import get_db
from app.api.v1.models.settings_model import CompanyCreate, CompanyUpdate
from app.api.v1.models.settings_response_model import CompanyResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_company,
    orm_get_all_companies,
    orm_get_company_by_code,
    orm_update_company_by_code,
    orm_delete_company_by_code,
)

from app.core.logging_config import get_service_logger
logger = get_service_logger("service.company")


router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Core_Settings"]
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_company(company: CompanyCreate, session: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"📥 [POST] Create company request received: {company.company_code}")

        cleaned = clean_create(company)  # ✅ replaces local clean_payload

        obj = await orm_create_company(session, cleaned)
        payload = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)

        return ResponseHandler.success(ResponseCode.SUCCESS["REGISTERED"][1], data={"company": payload})
    except Exception as e:
        logger.error(f"❌ Exception in create_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_all_companies(session: AsyncSession = Depends(get_db)):
    logger.info("📥 [GET] Read all companies")
    items = await orm_get_all_companies(session)

    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])

    payload = [CompanyResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(payload), "companies": payload},
    )


@router.get(
    "/search-by-code",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_company(company_code: str, session: AsyncSession = Depends(get_db)):
    logger.info(f"📥 [GET] Read company by code: {company_code}")
    obj = await orm_get_company_by_code(session, company_code)

    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

    payload = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"company": payload})


@router.put(
    "/update-by-code",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_company(company_code: str, company: CompanyUpdate, session: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"📥 [PUT] Update company: {company_code}")

        updated = clean_update(company)  # ✅ replaces local clean_payload(exclude_unset=True)

        obj = await orm_update_company_by_code(session, company_code, updated)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

        payload = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(ResponseCode.SUCCESS["UPDATED"][1], data={"company": payload})
    except Exception as e:
        logger.error(f"❌ Exception in update_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/delete-by-code",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_company(company_code: str, session: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"📥 [DELETE] Delete company: {company_code}")
        ok = await orm_delete_company_by_code(session, company_code)

        if not ok:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

        return ResponseHandler.success(
            f"Company with company_code {company_code} deleted.",
            data={"company_code": company_code},
        )
    except Exception as e:
        logger.error(f"❌ Exception in delete_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
