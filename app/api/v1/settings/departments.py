# # app/api/v1/settings/departments.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import DepartmentCreate, DepartmentUpdate
from app.api.v1.models.settings_response_model import (
    DepartmentResponse,
    DepartmentCreateEnvelope,
    DepartmentSearchEnvelope,
    DepartmentGetEnvelope,
    DepartmentUpdateEnvelope,
    DepartmentDeleteEnvelope,
)

from app.api.v1.services.settings_orm_service import (
    orm_create_department,
    orm_get_department_by_id,
    orm_update_department_by_id,
    orm_delete_department_by_id,
)

from app.db.models import Department

# ✅ DRY helpers (มาตรฐานเดียวกับ patients)
from app.utils.router_helpers import respond_list_paged, run_or_500, respond_one

import logging
logger = logging.getLogger("api.departments")


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/departments",
    tags=["Core_Settings"],
)


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"department": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_department(payload: DepartmentCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"department": {...}}
    """

    async def _work():
        obj = await orm_create_department(session, clean_create(payload))
        out = DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"department": out},
        )

    return await run_or_500(_work, logger=logger, log_prefix="departments.search: ")
    #return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "company_code": None, "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "departments": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_departments(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="department_code / department_name"),
    company_code: Optional[str] = Query(default=None, description="filter by company_code"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "departments": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY
    """
    filters = {"q": q, "company_code": company_code, "is_active": is_active}

    async def _work():
        where = [Department.is_active == is_active]

        if company_code:
            where.append(Department.company_code == company_code)

        if q:
            kw = f"%{q}%"
            where.append(or_(Department.department_code.ilike(kw), Department.department_name.ilike(kw)))

        count_stmt = select(func.count()).select_from(Department)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(Department)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Department.department_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="departments",
            model_cls=DepartmentResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work, logger=logger, log_prefix="departments.search: ")


@router.get(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"department": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    Response data shape:
    - {"department": {...}}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        obj = await orm_get_department_by_id(session, department_id)
        return respond_one(
            obj=obj,
            key="department",
            model_cls=DepartmentResponse,
            not_found_details={"department_id": str(department_id)},
        )

    return await run_or_500(_work, logger=logger, log_prefix="departments.search: ")


@router.put(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"department": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    session: AsyncSession = Depends(get_db),
):
    """
    Update (baseline = patients)
    Response data shape:
    - {"department": {...}}
    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        data = clean_update(payload)

        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "department_id": str(department_id)},
                status_code=422,
            )

        obj = await orm_update_department_by_id(session, department_id, data)
        return respond_one(
            obj=obj,
            key="department",
            model_cls=DepartmentResponse,
            not_found_details={"department_id": str(department_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work, logger=logger, log_prefix="departments.search: ")


@router.delete(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                data={"department_id": "<id>"},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    Response data shape:
    - {"department_id": "..."}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        ok = await orm_delete_department_by_id(session, department_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"department_id": str(department_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"department_id": str(department_id)},
        )

    return await run_or_500(_work, logger=logger, log_prefix="departments.search: ")



# # app/api/v1/settings/departments.py

# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, or_, func
# from uuid import UUID
# from typing import Optional

# from app.database.session import get_db
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, common_errors, success_example
# from app.api.v1.models.bookings_model import ErrorEnvelope
# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

# from app.api.v1.models.settings_model import DepartmentCreate, DepartmentUpdate
# from app.api.v1.models.settings_response_model import DepartmentResponse, DepartmentCreateEnvelope, DepartmentSearchEnvelope, DepartmentGetEnvelope, DepartmentUpdateEnvelope, DepartmentDeleteEnvelope
# from app.api.v1.services.settings_orm_service import (
#     orm_create_department,
#     orm_get_department_by_id,
#     orm_update_department_by_id,
#     orm_delete_department_by_id,
# )

# from app.db.models import Department

# from app.utils.router_helpers import (
#     respond_one,
#     respond_list_paged,
#     run_or_500,
# )


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/departments",
#     tags=["Core_Settings"],
# )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=DepartmentCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Registered successfully.', data={'department': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, include_500=True),
#     })
# async def create_department(payload: DepartmentCreate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await orm_create_department(session, clean_create(payload))
#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={
#                 "department": DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)
#             },
#         )

#     return await run_or_500(_work)


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=DepartmentSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'filters': {'q': ''}, 'paging': {'total': 0, 'limit': 50, 'offset': 0}, 'departments': []})),
#         **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
#     })
# async def search_departments(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="department_code / department_name"),
#     company_code: Optional[str] = Query(default=None),
#     is_active: bool = Query(default=True),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q, "company_code": company_code, "is_active": is_active}

#     async def _work():
#         where = [Department.is_active == is_active]

#         if company_code:
#             where.append(Department.company_code == company_code)

#         if q:
#             kw = f"%{q}%"
#             where.append(
#                 or_(
#                     Department.department_code.ilike(kw),
#                     Department.department_name.ilike(kw),
#                 )
#             )

#         count_stmt = select(func.count()).select_from(Department)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(Department)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Department.department_name.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="departments",
#             model_cls=DepartmentResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)


# @router.get(
#     "/{department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=DepartmentGetEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'department': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def read_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await orm_get_department_by_id(session, department_id)
#         return respond_one(
#             obj=obj,
#             key="department",
#             model_cls=DepartmentResponse,
#             not_found_details={"department_id": str(department_id)},
#         )

#     return await run_or_500(_work)


# @router.put(
#     "/{department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=DepartmentUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'department': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def update_department(
#     department_id: UUID,
#     payload: DepartmentUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_update_department_by_id(session, department_id, clean_update(payload))
#         return respond_one(
#             obj=obj,
#             key="department",
#             model_cls=DepartmentResponse,
#             not_found_details={"department_id": str(department_id)},
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#         )

#     return await run_or_500(_work)


# @router.delete(
#     "/{department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=DepartmentDeleteEnvelope,
#     responses={
#         **success_200_example(example=success_example(message='Deleted successfully.', data={'department_id': '<id>'})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def delete_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         ok = await orm_delete_department_by_id(session, department_id)
#         if not ok:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"department_id": str(department_id)}, status_code=404)

#         return ResponseHandler.success(
#             message=f"Department with ID {department_id} deleted.",
#             data={"department_id": str(department_id)},
#         )

#     return await run_or_500(_work)
