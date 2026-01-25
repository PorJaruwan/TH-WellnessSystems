# app/api/v1/patients/patients.py

from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import PatientCreate, PatientUpdate
from app.api.v1.services.patients_service import (
    list_patients,
    get_patient,
    search_patients,
    create_patient,
    patch_patient,
    delete_patient,
)

router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patient_Settings"],
)


@router.get("", response_class=UnicodeJSONResponse)
async def get_patients(
    db: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword: ชื่อ/นามสกุล/รหัส/โทร/id_card"),
    status: str = Query(default="", description="filter status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        if q or status:
            data = await search_patients(
                db,
                q_text=unquote(q),
                status=status,
                limit=limit,
                offset=offset,
            )
        else:
            data = await list_patients(db, limit=limit, offset=offset)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"total": len(data), "patients": data},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
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


@router.post("/create", response_class=UnicodeJSONResponse)
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


@router.patch("/update-by-id", response_class=UnicodeJSONResponse)
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


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
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
