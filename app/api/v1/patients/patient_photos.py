from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from uuid import uuid4, UUID
from fastapi import UploadFile, File, Form, APIRouter
from datetime import datetime
from pathlib import Path
from app.utils.ResponseHandler import UnicodeJSONResponse
#from supabase import create_client
#import os
#from urllib.parse import urlparse


router = APIRouter(
    prefix="/api/v1/patient_photos", 
    tags=["Patient_Settings"]
)

@router.post("/upload-photo")
async def upload_photo(
    patient_id: UUID = Form(...),
    file: UploadFile = File(...)
):
    contents = await file.read()
    file_id = str(uuid4())
    file_extension = Path(file.filename).suffix or ".jpg"
    file_name = f"{file_id}{file_extension}"

    # ✅ Step 1: ตรวจสอบว่ามีภาพเดิมอยู่ไหม
    existing_res = supabase.table("patient_photos").select("*").eq("patient_id", str(patient_id)).execute()
    existing_data = existing_res.data

    if existing_data:
        old_file_path = existing_data[0].get("file_path", "")
        if old_file_path:
            # ✅ Step 2: ดึงชื่อไฟล์จาก URL # ตัวอย่าง URL: https://xyz.supabase.co/storage/v1/object/public/patient-photos/abc.jpg
            from urllib.parse import urlparse
            parsed_url = urlparse(old_file_path)
            storage_prefix = "/storage/v1/object/public/"
            if parsed_url.path.startswith(storage_prefix):
                old_file_name = parsed_url.path.replace("/storage/v1/object/public/patient-photos/", "")
                #old_file_name = parsed_url.path.replace(storage_prefix, "")
                #print("📂 Correct delete path:", old_file_name)
                supabase.storage.from_("patient-photos").remove([old_file_name])
        # ✅ ลบ record เดิมจาก DB
        supabase.table("patient_photos").delete().eq("patient_id", str(patient_id)).execute()

        print("📂 Attempting to delete:", old_file_name)

    # ✅ Step 3: Upload ไฟล์ใหม่
    upload_res = supabase.storage.from_("patient-photos").upload(
        path=file_name,
        file=contents,
        file_options={"content-type": file.content_type}
    )

    upload_res_dict = upload_res if isinstance(upload_res, dict) else upload_res.__dict__
    if "status_code" in upload_res_dict and upload_res_dict["status_code"] >= 400:
        return UnicodeJSONResponse(
            status_code=500,
            content={"message": "Upload failed", "detail": upload_res_dict.get("message", "Unknown error")},
        )

    public_url = supabase.storage.from_("patient-photos").get_public_url(file_name)

    # ✅ Step 4: บันทึกข้อมูลรูปใหม่
    insert_res = supabase.table("patient_photos").insert({
        "patient_id": str(patient_id),
        "file_path": public_url,
        "uploaded_at": datetime.utcnow().isoformat(),
    }).execute()

    insert_dict = insert_res if isinstance(insert_res, dict) else insert_res.__dict__

    if insert_dict.get("data") is None or insert_dict.get("status_code", 200) >= 400:
        return UnicodeJSONResponse(
            status_code=500,
            content={"message": "Insert DB failed", "detail": insert_dict.get("message", "Unknown error")},
        )

    return {
        "message": "Upload successful",
        "file_url": public_url,
    }