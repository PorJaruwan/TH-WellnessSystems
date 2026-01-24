from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import SaleStaffCreate, SaleStaffUpdate
from app.api.v1.services.patients_service import (
    create_sale_staff,
    get_all_sale_staff,
    get_sale_staff_by_id,
    update_sale_staff_by_id,
    delete_sale_staff_by_id,
)

router = APIRouter(
    prefix="/api/v1/sale_staff",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_sale_staff_by_id(
    saleStaff: SaleStaffCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await create_sale_staff(db, saleStaff)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"saleStaff": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_sale_staff_by_all(
    db: AsyncSession = Depends(get_db),
):
    items = await get_all_sale_staff(db)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(items), "saleStaff": items},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_sale_staff_by_id(
    sale_staff_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_sale_staff_by_id(db, sale_staff_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"sale_staff_id": str(sale_staff_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"saleStaff": item},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_sale_staff(
    sale_staff_id: UUID,
    saleStaff: SaleStaffUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await update_sale_staff_by_id(db, sale_staff_id, saleStaff)
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"sale_staff_id": str(sale_staff_id)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"saleStaff": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_sale_staff(
    sale_staff_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_sale_staff_by_id(db, sale_staff_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"sale_staff_id": str(sale_staff_id)},
            )
        return ResponseHandler.success(
            message=f"Sale staff with ID {sale_staff_id} deleted.",
            data={"sale_staff_id": str(sale_staff_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# from app.core.config import get_settings
# settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# from fastapi import APIRouter, Request, HTTPException, Response
# from fastapi.encoders import jsonable_encoder
# from uuid import UUID

# from app.api.v1.models.patients_model import SaleStaffCreateModel, SaleStaffUpdateModel
# from app.api.v1.services.patients_service import (
#     create_sale_staff, get_all_sale_staff, get_sale_staff_by_id,
#     update_sale_staff_by_id, delete_sale_staff_by_id
# )


# router = APIRouter(
#     prefix="/api/v1/sale_staff",
#     tags=["Patient_Settings"]
# )

# @router.post("/create-by-id", response_class=UnicodeJSONResponse)
# def create_sale_staff_by_id(saleStaff: SaleStaffCreateModel):
#     try:
#         data = jsonable_encoder(saleStaff)
#         cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
#         res = create_sale_staff(cleaned_data)
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"saleStaff": res.data[0]}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_sale_staff_by_all():
#     res = get_all_sale_staff()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "saleStaff": res.data}
#     )

# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_sale_staff_by_id(sale_staff_id: UUID):
#     res = get_sale_staff_by_id(sale_staff_id)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"sale_staff_id": str(sale_staff_id)})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"saleStaff": res.data[0]}
#     )

# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_sale_staff_by_id(sale_staff_id: UUID, saleStaff: SaleStaffUpdateModel):
#     updated = {
#         "sale_staff_name": saleStaff.sale_staff_name,
#         "department": saleStaff.department,
#     }
#     res = update_sale_staff_by_id(sale_staff_id, updated)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"sale_staff_id": str(sale_staff_id)})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["UPDATED"][1],
#         data={"saleStaff": res.data[0]}
#     )

# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_sale_staff_by_id(sale_staff_id: UUID):
#     try:
#         res = delete_sale_staff_by_id(sale_staff_id)
#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"sale_staff_id": str(sale_staff_id)})
#         return ResponseHandler.success(
#             message=f"Sale staff with ID {sale_staff_id} deleted.",
#             data={"sale_staff_id": str(sale_staff_id)}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
