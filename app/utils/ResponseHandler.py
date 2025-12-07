from fastapi.responses import JSONResponse, Response
from typing import Optional, Dict
import json
from fastapi.encoders import jsonable_encoder

class ResponseCode:
    AUTH = {
        "INVALID_CREDENTIALS": ("AUTH_001", "Invalid credentials provided."),
        "UNAUTHORIZED": ("AUTH_002", "Unauthorized access.")
    }

    VALIDATION = {
        "MISSING_FIELDS": ("VALID_001", "Missing required fields."),
        "INVALID_EMAIL": ("VALID_002", "Invalid email format.")
    }

    DATABASE = {
        "CONNECTION_FAILED": ("DB_001", "Failed to connect to database."),
        "DUPLICATE_ENTRY": ("DB_002", "Duplicate entry found.")
    }
   
    API = {
        "API_NOT_FOUND": ("API_001", "Endpoint not found.")
    }

    SYSTEM = {
        "INTERNAL_ERROR": ("SYS_001", "Internal server error.")
    }

    SUCCESS = {
        "REGISTERED": ("SUCCESS_001", "User registered successfully."),
        "UPDATED": ("SUCCESS_002", "Data updated successfully."),
        "RETRIEVED": ("SUCCESS_003", "Data retrieved successfully."),
        "DELETED": ("SUCCESS_004", "Data deleted successfully.")
    }

    DATA = {
        "NOT_FOUND": ("DATA_001", "Data not found."),
        "EMPTY": ("DATA_002", "Data empty.")
    }

class ResponseHandler:
    @staticmethod
    def success(message: str, data: Optional[dict] = None):
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": "success",
                "message": message,
                "data": data or {}
            })
        )

    # @staticmethod
    # def error(code: str, message: str, details: Optional[Dict] = None, status_code: int = 400):
    #     return JSONResponse(
    #         status_code=status_code,
    #         content=json.loads(json.dumps({
    #             "status": "error",
    #             "error_code": code,
    #             "message": message,
    #             "details": details or {}
    #         }, ensure_ascii=False, default=str))
    #     )
    
    @staticmethod
    def error(code: str, message: str, details: Optional[Dict] = None, status_code: int = 400):
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder({
                "status": "error",
                "error_code": code,
                "message": message,
                "details": details or {}
            })
        )

# ✅ ตั้งค่า Response เป็น JSON ที่รองรับ UTF-8
# กำหนดรูปแบบ Response ให้รองรับภาษาไทย (UTF-8)
# 🧾 สร้างคลาส Response แบบ custom เพื่อให้รองรับ UTF-8 โดยเฉพาะภาษาไทย
class UnicodeJSONResponse(Response):
    media_type = "application/json; charset=utf-8"

# แปลงเนื้อหา response ให้เป็น JSON พร้อมรองรับภาษาไทย
# 🔄 Override เมธอด render ของ FastAPI เพื่อแปลงเนื้อหาให้ออกมาเป็น JSON ที่ใช้ UTF-8
    def render(self, content: any) -> bytes:
        return json.dumps(
            jsonable_encoder(content),  # ✅ ป้องกัน datetime, UUID, Pydantic object
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")