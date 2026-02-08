# app/api/v1/settings/companies.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.core.logging_config import get_service_logger
from app.utils.openapi_responses import success_200_example, success_example, common_errors


from app.api.v1.models.settings_model import CompanyCreate, CompanyUpdate
from app.api.v1.models.settings_response_model import (
    CompanyResponse,
    CompanyCreateEnvelope,
    CompanyUpdateEnvelope,
    CompanyDeleteEnvelope,
    CompanySearchEnvelope,
)

# ✅ ใช้ ORM service เดิม (ไม่เปลี่ยน business logic)
from app.api.v1.services.settings_orm_service import (
    orm_create_company,
    orm_update_company_by_code,
    orm_delete_company_by_code,
)

# ✅ ORM model สำหรับ query search
from app.db.models import Company

# ✅ DRY helpers (มาตรฐานเดียวกับ patients)
from app.utils.router_helpers import respond_list_paged, run_or_500, respond_one

logger = get_service_logger("service.company")

router = APIRouter(
    # ✅ CHANGED: ให้เหมือน patients baseline -> prefix ต้องมี /api/v1/...
    prefix="/companies",
    tags=["Core_Settings"],
)


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=CompanyCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="REGISTERED",
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={
                    # ✅ baseline: create/update/by-id => singular key
                    "company": {
                        "company_code": "WP",
                        "company_name": "WellPlus",
                        "company_name_en": "WellPlus",
                        "vat_rate": 0,
                        "is_active": True,
                    }
                },
            ),
        ),
        **common_errors(error_model=dict, include_500=True),
    },
)
async def create_company(payload: CompanyCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)

    Response data shape:
    - {"company": {...}}
    """

    async def _work():
        logger.info(f"📥 [POST] Create company request received: {payload.company_code}")

        data = clean_create(payload)
        obj = await orm_create_company(session, data)

        out = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"company": out},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.create: ")


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=CompanySearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="RETRIEVED",
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    # ✅ CHANGED: baseline search => filters + paging + companies[]
                    "filters": {"q": "", "is_active": True},
                    "paging": {"total": 1, "limit": 50, "offset": 0},
                    "companies": [
                        {
                            "company_code": "WP",
                            "company_name": "WellPlus",
                            "company_name_en": "WellPlus",
                            "vat_rate": 0,
                            "is_active": True,
                        }
                    ],
                },
            ),
        ),
        **common_errors(error_model=dict, empty=True, include_500=True),
    },
)
async def search_companies(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): company_code/company_name/company_name_en"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search / List (baseline = patients)

    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "companies": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY
    - order_by must be deterministic
    """
    # ✅ CHANGED: baseline ต้องส่ง filters กลับไปเสมอ
    filters = {"q": q, "is_active": is_active}

    async def _work():
        logger.info(f"📥 [GET] Search companies | filters={filters} | limit={limit} offset={offset}")

        # ---------- common WHERE ----------
        where_clauses = [Company.is_active == is_active]

        if q:
            kw = f"%{q}%"
            where_clauses.append(
                or_(
                    Company.company_code.ilike(kw),
                    Company.company_name.ilike(kw),
                    func.coalesce(Company.company_name_en, "").ilike(kw),
                )
            )

        # ---------- total COUNT(*) ----------
        count_stmt = select(func.count()).select_from(Company)
        for cond in where_clauses:
            count_stmt = count_stmt.where(cond)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        # ---------- page query ----------
        stmt = select(Company)
        for cond in where_clauses:
            stmt = stmt.where(cond)

        # ✅ deterministic order_by (baseline)
        stmt = stmt.order_by(Company.company_name.asc()).limit(limit).offset(offset)

        res = await session.execute(stmt)
        items = res.scalars().all()

        # ✅ CHANGED: ให้ helper จัดรูปแบบ response แบบ patients (รวม EMPTY policy)
        return respond_list_paged(
            items=items,
            plural_key="companies",
            model_cls=CompanyResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.search: ")


@router.put(
    "/{company_code}",
    response_class=UnicodeJSONResponse,
    response_model=CompanyUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="UPDATED",
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={
                    "company": {
                        "company_code": "WP",
                        "company_name": "WellPlus",
                        "company_name_en": "WellPlus",
                        "vat_rate": 0,
                        "is_active": True,
                    }
                },
            ),
        ),
        **common_errors(error_model=dict, not_found=True, include_500=True),
    },
)
async def update_company(company_code: str, payload: CompanyUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)

    Response data shape:
    - {"company": {...}}

    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        logger.info(f"📥 [PUT] Update company: {company_code}")

        # ✅ CHANGED: baseline rule -> payload ว่าง = 422
        data = clean_update(payload)
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "company_code": company_code},
                status_code=422,
            )

        obj = await orm_update_company_by_code(session, company_code, data)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"company_code": company_code},
                status_code=404,
            )

        out = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"company": out},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.update: ")


@router.delete(
    "/{company_code}",
    response_class=UnicodeJSONResponse,
    response_model=CompanyDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="DELETED",
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                # ✅ baseline: delete => return identifier only
                data={"company_code": "WP"},
            ),
        ),
        **common_errors(error_model=dict, not_found=True, include_500=True),
    },
)
async def delete_company(company_code: str, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)

    Response data shape:
    - {"company_code": "..."}

    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        logger.info(f"📥 [DELETE] Delete company: {company_code}")

        ok = await orm_delete_company_by_code(session, company_code)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"company_code": company_code},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"company_code": company_code},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.delete: ")
