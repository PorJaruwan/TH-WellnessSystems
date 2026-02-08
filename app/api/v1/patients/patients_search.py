# app/api/v1/patients/patients_search.py

from __future__ import annotations

from urllib.parse import unquote
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models._envelopes.patients_search_envelopes import PatientsSearchListEnvelope
from app.api.v1.models.patient_profiles_model import PatientSearchItemDTO
from app.api.v1.services.patient_crud_service import list_patients, search_patients

router = APIRouter(prefix="/patients", tags=["Patient_Profiles"])

DEFAULT_SORT_BY = "created_at"     # ✅ แนะนำ default list view
DEFAULT_SORT_ORDER = "desc"

@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=PatientsSearchListEnvelope,
    response_model_exclude_none=True,
)
async def patients_search_endpoint(
    db: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword: ชื่อ/นามสกุล/รหัส/โทร/id_card"),
    status: str = Query(default="", description="filter status"),
    is_active: Optional[bool] = Query(default=True, description="default true"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        q2 = unquote(q) if q else ""

        filters = {
            "q": q2 or None,
            "status": status or None,
            "is_active": is_active,
        }

        # ✅ ใช้ search_patients เสมอ (ห้ามเรียก list_patients)
        items, total = await search_patients(
            db=db,
            q_text=q2,
            status=status,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

        if total == 0:
            return ResponseHandler.error(
                *ResponseCode.DATA["EMPTY"],
                details={"filters": filters},
            )

        typed_items = [
            PatientSearchItemDTO.model_validate(x).model_dump()
            for x in items
        ]

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "filters": filters,
                "sort": {
                    "by": sort_by,
                    "order": sort_order,
                },
                "paging": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                },
                "items": typed_items,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=PatientsSearchListEnvelope,
#     response_model_exclude_none=True,
# )
# async def patients_search_endpoint(
#     db: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword: ชื่อ/นามสกุล/รหัส/โทร/id_card"),
#     status: str = Query(default="", description="filter status"),
#     is_active: Optional[bool] = Query(default=True, description="default true"),
#     sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
#     sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     try:
#         q2 = unquote(q) if q else ""
#         filters = {"q": q2 or None, "status": status or None, "is_active": is_active}

#         if (q2 and q2.strip()) or status:
#             items, total = await search_patients(
#                 db,
#                 q_text=q2,
#                 status=status,
#                 is_active=is_active,
#                 limit=limit,
#                 offset=offset,
#                 sort_by=sort_by,
#                 sort_order=sort_order,
#             )
#             items, total = await list_patients(
#                 db,
#                 is_active=is_active,
#                 limit=limit,
#                 offset=offset,
#                 sort_by=sort_by,
#                 sort_order=sort_order,
#             )

#         if total == 0:
#             return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

#         typed_items = [PatientSearchItemDTO.model_validate(x).model_dump() for x in items]

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={
#                 "filters": filters,
#                 "sort": {"by": sort_by, "order": sort_order},
#                 "paging": {"total": total, "limit": limit, "offset": offset},
#                 "items": typed_items,
#             },
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
