# app/api/v1/settings/companies.py
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import CompanyCreateModel, CompanyUpdateModel
from app.api.v1.services.settings_service import (
    post_company, get_all_companies, get_company_by_code,
    put_company_by_code, delete_company_by_code
)

# logging
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.company")

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["General_Settings"]
)

# ✅ CREATE
@router.post("/create-by-code", response_class=UnicodeJSONResponse)
def create_company(companies: CompanyCreateModel):
    try:
        logger.info(f"📥 [POST] Create company request received: {companies.company_code}")
        data = jsonable_encoder(companies)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = post_company(cleaned_data)

        if not res.data:
            logger.warning(f"⚠️ Failed to insert company: {companies.company_code}")
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        logger.info(f"✅ Company created: {res.data[0].get('company_code')}")
        return ResponseHandler.success(ResponseCode.SUCCESS["REGISTERED"][1], data={"companies": res.data[0]})

    except Exception as e:
        logger.error(f"❌ Exception in create_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_companies():
    logger.info("📥 [GET] Read all companies")
    res = get_all_companies()

    if not res.data:
        logger.warning("⚠️ No companies found")
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])

    logger.info(f"✅ Retrieved {len(res.data)} companies")
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "companies": res.data})


# ✅ READ BY CODE
@router.get("/search-by-code", response_class=UnicodeJSONResponse)
def read_company(company_code: str):
    logger.info(f"📥 [GET] Read company by code: {company_code}")
    res = get_company_by_code(company_code)

    if not res.data:
        logger.warning(f"⚠️ Company not found for code: {company_code}")
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

    logger.info(f"✅ Retrieved company: {company_code}")
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"companies": res.data[0]})


# ✅ UPDATE BY CODE
@router.put("/update-by-code", response_class=UnicodeJSONResponse)
def update_company(company_code: str, companies: CompanyUpdateModel):
    try:
        logger.info(f"📥 [PUT] Update company: {company_code}")
        updated = jsonable_encoder(companies)
        res = put_company_by_code(company_code, updated)

        if not res.data:
            logger.warning(f"⚠️ Cannot update. Company not found: {company_code}")
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

        logger.info(f"✅ Company updated: {company_code}")
        return ResponseHandler.success(ResponseCode.SUCCESS["UPDATED"][1], data={"companies": res.data[0]})

    except Exception as e:
        logger.error(f"❌ Exception in update_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ DELETE BY CODE
@router.delete("/delete-by-code", response_class=UnicodeJSONResponse)
def delete_company(company_code: str):
    try:
        logger.info(f"📥 [DELETE] Delete company: {company_code}")
        res = delete_company_by_code(company_code)

        if not res.data:
            logger.warning(f"⚠️ Cannot delete. Company not found: {company_code}")
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"company_code": company_code})

        logger.info(f"✅ Company deleted: {company_code}")
        return ResponseHandler.success(f"Company with company_code {company_code} deleted.", data={"company_code": company_code})

    except Exception as e:
        logger.error(f"❌ Exception in delete_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
