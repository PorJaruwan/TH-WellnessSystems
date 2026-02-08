# app/api/v1/patients/patients.py

from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import PatientCreate, PatientUpdate
from app.api.v1.models._envelopes.patients_profile_envelopes import (
    PatientCreateEnvelope,
    PatientByIdEnvelope,
    PatientUpdateEnvelope,
    PatientDeleteEnvelope,
)

#from app.api.v1.services.patient_crud_service import list_patients, search_patients
from app.api.v1.services.patient_crud_service import (
    get_patient,
    create_patient,
    patch_patient,
    delete_patient,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/patients",
    tags=["Patient_Profiles"],
)

@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=PatientCreateEnvelope,
    response_model_exclude_none=True,
)
async def post_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        created = await create_patient(db, payload)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient": created},
        )
    except ValueError as e:
        # unique constraint / integrity error
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/search-old",
#     response_class=UnicodeJSONResponse,
#     response_model=PatientSearchEnvelope,
#     response_model_exclude_none=True,
# )
# async def get_patients(
#     db: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword: ชื่อ/นามสกุล/รหัส/โทร/id_card"),
#     status: str = Query(default="", description="filter status"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     """
#     List/Search Patients (มาตรฐานเดียวกับ locations)
#     - total   : จำนวนทั้งหมดจริง (ก่อน limit/offset)
#     - count   : จำนวนรายการในหน้านี้
#     - limit   : page size
#     - offset  : page offset
#     - filters : เงื่อนไขที่ใช้ค้นหา (ช่วย debug/UI)
#     - policy  : ถ้าไม่พบข้อมูล -> DATA.EMPTY
#     """
#     try:
#         filters = {
#             "q": unquote(q),
#             "status": status,
#         }

#         # เลือก service ตามเงื่อนไขค้นหา
#         if filters["q"] or status:
#             items, total = await search_patients(
#                 db,
#                 q_text=filters["q"],
#                 status=status,
#                 limit=limit,
#                 offset=offset,
#             )
#         else:
#             items, total = await list_patients(
#                 db,
#                 limit=limit,
#                 offset=offset,
#             )

#         # ✅ Policy แบบ A (เหมือน locations)
#         # ถ้าไม่มีข้อมูลเลย -> DATA.EMPTY
#         if total == 0:
#             return ResponseHandler.error(
#                 *ResponseCode.DATA["EMPTY"],
#                 details={"filters": filters},
#             )

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={
#                 "total": total,        # จำนวนทั้งหมดจริง
#                 "count": len(items),   # จำนวนในหน้านี้
#                 "limit": limit,
#                 "offset": offset,
#                 "filters": filters,    # ช่วย debug / UI
#                 "patients": items,
#             },
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/patient_id",
    response_class=UnicodeJSONResponse,
    response_model=PatientByIdEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_by_id(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        p = await get_patient(db, patient_id)
        if not p:
            raise HTTPException(status_code=404, detail="patient not found")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"patient": p},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientUpdateEnvelope,
    response_model_exclude_none=True,
)
async def patch_patient_by_id(
    patient_id: UUID,
    payload: PatientUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await patch_patient(db, patient_id, payload)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patient": updated},
        )
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        if "exists" in msg or "duplicate" in msg:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_patient_by_id(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted_id = await delete_patient(db, patient_id)
        return ResponseHandler.success(
            message=f"Patient with ID {deleted_id} deleted.",
            data={"patient_id": str(deleted_id)},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
