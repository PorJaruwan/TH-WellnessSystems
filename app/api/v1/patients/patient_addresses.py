from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.patients_model import AddressesCreateModel, AddressesUpdateModel
from app.api.v1.services.patients_service import (
    get_all_patient_addresses, get_patient_address_by_id,
    get_patient_address_by_code_type, create_patient_address,
    update_patient_address_by_id, delete_patient_address_by_id
)

router = APIRouter(
    prefix="/api/v1/patient_addresses",
    tags=["Patient_Settings"]
)


# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_patient_address_by_all():
    res = get_all_patient_addresses()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "patient_addresses": res.data}
    )

# ✅ READ BY patient_id
@router.get("/search-by-patient-id", response_class=UnicodeJSONResponse)
def read_patient_address_by_id(addr_id: UUID):
    res = get_patient_address_by_id(addr_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(addr_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patient_addresses": res.data[0]}
    )

# ✅ READ BY patient_code + address_type
@router.get("/search-by-code-type", response_class=UnicodeJSONResponse)
def get_patient_address_by_patientCode_and_patientType(patient_code: str, address_type: str):
    patient_id, addr_res = get_patient_address_by_code_type(patient_code, address_type)
    if not patient_id:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_code": patient_code})
    if not addr_res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "patient_code": patient_code,
            "address_type": address_type
        })
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "patient_code": patient_code,
            "address_type": address_type,
            "patient_address": addr_res.data[0]
        }
    )

# ✅ CREATE BY Patient & Address_Type
@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_patient_address_by_id(addresses: AddressesCreateModel):
    try:
        data = jsonable_encoder(addresses)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_patient_address(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"addresses": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ UPDATE Patient
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_patient_address_by_id(addressId: UUID, addresses: AddressesUpdateModel):
    try:
        updated = {
            "address": addresses.address,
            "street": addresses.street,
            "city": addresses.city,
            "state": addresses.state,
            "postal_code": addresses.postal_code,
            "country": addresses.country,
        }
        res = update_patient_address_by_id(addressId, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"addressId": str(addressId)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"addresses": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ DELETE Patient
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_patient_address_by_id(addrId: UUID):
    try:
        res = delete_patient_address_by_id(addrId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"addrId": str(addrId)})
        return ResponseHandler.success(
            message=f"addresses with addrId {addrId} deleted.",
            data={"addrId": str(addrId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))