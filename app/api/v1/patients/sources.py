from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.v1.models.patients_model import SourceCreate, SourceUpdate
from app.api.v1.services.patients_service import (
    post_source_service,
    get_all_source_service,
    get_source_by_id_service,
    put_source_by_id_service,
    delete_source_by_id_service,
    generate_source_update_payload,
    format_source_results,
)
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

router = APIRouter(
    prefix="/api/v1/sources",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_source_by_id(
    sources: SourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new source (async, ORM-aware service)."""
    try:
        res = await post_source_service(db, sources)
        if res is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"sources": res},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_source_by_all(
    db: AsyncSession = Depends(get_db),
):
    raw = await get_all_source_service(db)
    if not raw:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    result_list = format_source_results(raw)

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(result_list), "sources": result_list},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_source_by_id(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_source_by_id_service(db, source_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"source_id": str(source_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"sources": item},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_source_by_id(
    source_id: UUID,
    sourc: SourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated = generate_source_update_payload(sourc)
    res = await put_source_by_id_service(db, source_id, updated)
    if res is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"source_id": str(source_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"sources": res},
    )


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_source_by_id(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_source_by_id_service(db, source_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"source_id": str(source_id)},
            )
        return ResponseHandler.success(
            message=f"source with ID {source_id} deleted.",
            data={"source_id": str(source_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




