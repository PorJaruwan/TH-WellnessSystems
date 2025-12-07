from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import json
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from pathlib import Path
from typing import Optional


router = APIRouter(
    prefix="/api/v1/users",
    tags=["User_Settings"]
)

# Pydantic model สำหรับ user
class UsersModel(BaseModel):
    id: int
    name: str
    email: str

# Fake database (จำลองข้อมูล)
from uuid import uuid4
from datetime import datetime

fake_users_db = [
    {
        "id": 1,
        "user_id": 1,
        "username": "alice123",
        "full_name": "อลิซ วันเดอร์แลนด์",  # เปลี่ยนเป็นภาษาไทย
        "phone_number": "0812345678",  # แก้ไข typo จาก phone_numbe เป็น phone_number
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "user_id": 2,
        "username": "bob456",
        "full_name": "บ็อบ บิลเดอร์",  # เปลี่ยนเป็นภาษาไทย
        "phone_number": "0823456789",  # แก้ไข typo จาก phone_numbe เป็น phone_number
        "role": "user",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]

# ✅ GET all users
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_users():
    if not fake_users_db:
        return ResponseHandler.error(
            *ResponseCode.DATA["EMPTY"],
            details={}
        )

    return ResponseHandler.success(
        message="ดึงข้อมูลผู้ใช้สำเร็จ",  # เปลี่ยนเป็นภาษาไทย
        data={
            "total": len(fake_users_db),
            "users": fake_users_db
        }
    )

# ✅ GET user by ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_user(user_id: int):    
    user = next((u for u in fake_users_db if u["id"] == user_id), None)

    if user:
        return ResponseHandler.success(
            message="ดึงข้อมูลผู้ใช้สำเร็จ",  # เปลี่ยนเป็นภาษาไทย
            data={"user": user}
        )

    return ResponseHandler.error(
        *ResponseCode.DATA["NOT_FOUND"],
        details={"user_id": user_id}
    )

# ✅ POST user (สร้างผู้ใช้ใหม่)
from pydantic import BaseModel, EmailStr

class UsersCreateModel(BaseModel):
    id: int
    name: str
    email: EmailStr

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_user(user: UsersCreateModel):
    # ตรวจสอบว่าผู้ใช้มีอยู่แล้วหรือไม่ (id หรือ email ซ้ำ)
    if any(u["id"] == user.id or u.get("email") == user.email for u in fake_users_db):
        return ResponseHandler.error(
            *ResponseCode.DATABASE["DUPLICATE_ENTRY"],
            details={"user_id": user.id, "email": user.email}
        )

    # เพิ่มผู้ใช้ใหม่
    new_user = {
        "id": user.id,
        "user_id": user.id,
        "username": user.name.lower().replace(" ", ""),
        "full_name": user.name,
        "phone_number": "",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    fake_users_db.append(new_user)

    return ResponseHandler.success(
        message="สร้างผู้ใช้ใหม่สำเร็จ",  # เปลี่ยนเป็นภาษาไทย
        data={"user": new_user}
    )

# ✅ PUT user by ID (อัปเดตข้อมูลผู้ใช้)
class UsersUpdateModel(BaseModel):
    name: str

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_user(user_id: int, user: UsersUpdateModel):
    for idx, u in enumerate(fake_users_db):
        if u["id"] == user_id:
            fake_users_db[idx]["full_name"] = user.name
            fake_users_db[idx]["updated_at"] = datetime.now().isoformat()
            return ResponseHandler.success(
                message="อัปเดตข้อมูลผู้ใช้สำเร็จ",  # เปลี่ยนเป็นภาษาไทย
                data={"user": fake_users_db[idx]}
            )

    return ResponseHandler.error(
        *ResponseCode.DATA["NOT_FOUND"],
        details={"user_id": user_id}
    )

# ✅ DELETE user by ID  
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_user(user_id: int):
    global fake_users_db

    # ตรวจสอบว่าผู้ใช้นี้มีอยู่หรือไม่
    existing_user = next((u for u in fake_users_db if u["id"] == user_id), None)

    if not existing_user:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_id": user_id})

    # ลบ user และอัปเดต fake_users_db
    fake_users_db = [u for u in fake_users_db if u["id"] != user_id]

    return ResponseHandler.success(
        message=f"ลบผู้ใช้ ID {user_id} สำเร็จ",  # เปลี่ยนเป็นภาษาไทย
        data={"user_id": user_id}
    )