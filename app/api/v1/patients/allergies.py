#app.
from app.core.config import get_settings
settings = get_settings()  # ✅ load settings (คงไว้ตามไฟล์เดิม)

from typing import Optional
from fastapi import Query
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import AllergyCreate, AllergyUpdate
from app.api.v1.services.patients_service import (
    create_allergy,
    get_all_allergies,
    get_allergy_by_id,
    update_allergy_by_id,
    delete_allergy_by_id,
)

# ✅ DRY / มาตรฐานเดียวกับ locations
from app.utils.payload_cleaner import clean_create, clean_update

router = APIRouter(
    prefix="/api/v1/allergies",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_allergy_by_id(
    allergy: AllergyCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create: single => {"allergy": {...}}
    """
    try:
        # ✅ ทำให้เหมือน locations: clean payload (""->None, drop audit fields)
        obj = await create_allergy(db, clean_create(allergy))
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"allergy": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/search", response_class=UnicodeJSONResponse)
# async def read_allergy_by_all(
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     List: list => {"total": n, "allergies": [...]}
#     Policy A: ว่าง => DATA.EMPTY
#     """
#     allergies = await get_all_allergies(db)

#     if not allergies:
#         return ResponseHandler.error(
#             *ResponseCode.DATA["EMPTY"],
#             details={"filters": {}},  # ✅ เผื่อ debug/UI ให้เหมือน locations
#         )

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={
#             "total": len(allergies),
#             "filters": {},          # ✅ เผื่อ debug/UI
#             "allergies": allergies  # ✅ key พหูพจน์ให้เป็นมาตรฐาน
#         },
#     )

@router.get("/search", response_class=UnicodeJSONResponse)
async def search_allergies(
    db: AsyncSession = Depends(get_db),
    allergy_name: Optional[str] = Query(
        default=None, description="filter by allergy name (partial match)"
    ),
    allergy_type: Optional[str] = Query(
        default=None, description="filter by allergy type เช่น drug / food / other"
    ),
    is_active: bool = Query(
        default=True, description="filter active/inactive (default=true)"
    ),
):
    """
    List/Search Allergies
    - parameters: allergy_name, allergy_type, is_active
    - response: { total, filters, allergies }
    - policy A: ว่าง => DATA.EMPTY
    """

    filters = {
        "allergy_name": allergy_name,
        "allergy_type": allergy_type,
        "is_active": is_active,
    }

    allergies = await get_all_allergies(
        db,
        allergy_name=allergy_name,
        allergy_type=allergy_type,
        is_active=is_active,
    )

    if not allergies:
        return ResponseHandler.error(
            *ResponseCode.DATA["EMPTY"],
            details={"filters": filters},
        )

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "total": len(allergies),
            "filters": filters,
            "allergies": allergies,
        },
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_allergy_by_id(
    allergy_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Read-by-id: single => {"allergy": {...}}
    """
    allergy = await get_allergy_by_id(db, allergy_id)
    if allergy is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"allergy_id": str(allergy_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"allergy": allergy},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_allergy(
    allergy_id: UUID,
    allergy: AllergyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update: single => {"allergy": {...}}
    """
    try:
        # ✅ ทำให้เหมือน locations: clean update payload
        obj = await update_allergy_by_id(db, allergy_id, clean_update(allergy))
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"allergy_id": str(allergy_id)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"allergy": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_allergy(
    allergy_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete: data => {"allergy_id": "..."} (snake_case)
    """
    try:
        deleted = await delete_allergy_by_id(db, allergy_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"allergy_id": str(allergy_id)},
            )
        return ResponseHandler.success(
            message=f"Allergy with id {allergy_id} deleted.",
            data={"allergy_id": str(allergy_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
