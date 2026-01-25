# app/api/v1/settings/companies.py

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.core.logging_config import get_service_logger

from app.api.v1.models.settings_model import CompanyCreate, CompanyUpdate
from app.api.v1.models.settings_response_model import CompanyResponse

from app.api.v1.services.settings_orm_service import (
    orm_create_company,
    orm_get_company_by_code,
    orm_update_company_by_code,
    orm_delete_company_by_code,
)

# ✅ ORM model สำหรับ query search
from app.db.models import Company

# ✅ DRY helpers (งานซ้ำ: list response + exception wrapper)
from app.utils.router_helpers import respond_list_paged, run_or_500

logger = get_service_logger("service.company")

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Core_Settings"],
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_company(payload: CompanyCreate, session: AsyncSession = Depends(get_db)):
    """
    Create: single => {"company": {...}}
    """
    async def _work():
        logger.info(f"📥 [POST] Create company request received: {payload.company_code}")

        data = clean_create(payload)
        obj = await orm_create_company(session, data)
        out = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"company": out},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.create: ")


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_companies(
    session: AsyncSession = Depends(get_db),
    q: str = Query(
        default="",
        description="keyword (like): company_code/company_name/company_name_en",
    ),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    List/Search (มาตรฐานเดียวกับ patients.py)
    - list => {"total": N, "count": n, "limit": L, "offset": O, "filters": {...}, "companies": [...]}
    - policy A: ว่าง => DATA.EMPTY
    """
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
        total = (await session.execute(count_stmt)).scalar_one()

        # ---------- page query ----------
        stmt = select(Company)
        for cond in where_clauses:
            stmt = stmt.where(cond)

        stmt = (
            stmt.order_by(Company.company_name.asc())
            .limit(limit)
            .offset(offset)
        )

        res = await session.execute(stmt)
        items = res.scalars().all()

        # ✅ DRY: standard list response + policy A + serialize
        return respond_list_paged(
            items=items,
            plural_key="companies",
            model_cls=CompanyResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.search: ")


@router.put(
    "/update-by-code",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_company(company_code: str, payload: CompanyUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update: single => {"company": {...}}
    """
    async def _work():
        logger.info(f"📥 [PUT] Update company: {company_code}")

        data = clean_update(payload)

        obj = await orm_update_company_by_code(session, company_code, data)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"company_code": company_code},
            )

        out = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"company": out},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.update: ")


@router.delete(
    "/delete-by-code",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_company(company_code: str, session: AsyncSession = Depends(get_db)):
    """
    Delete: data => {"company_code": "..."}
    """
    async def _work():
        logger.info(f"📥 [DELETE] Delete company: {company_code}")

        ok = await orm_delete_company_by_code(session, company_code)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"company_code": company_code},
            )

        return ResponseHandler.success(
            message=f"Company with company_code {company_code} deleted.",
            data={"company_code": company_code},
        )

    return await run_or_500(_work, logger=logger, log_prefix="companies.delete: ")


###---ใช้ def search_companies แทน
# @router.get(
#     "/search-by-code",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def read_company(company_code: str, session: AsyncSession = Depends(get_db)):
#     """
#     Read-by-code: single => {"company": {...}}
#     """
#     logger.info(f"📥 [GET] Read company by code: {company_code}")

#     obj = await orm_get_company_by_code(session, company_code)
#     if not obj:
#         return ResponseHandler.error(
#             *ResponseCode.DATA["NOT_FOUND"],
#             details={"company_code": company_code},
#         )

#     out = CompanyResponse.model_validate(obj).model_dump(exclude_none=True)
#     return ResponseHandler.success(
#         ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"company": out},
#     )
