# app/api/v1/services/patient_photos_storage_service.py
from __future__ import annotations

from uuid import uuid4
from pathlib import Path
from urllib.parse import urlparse

from app.services.supabase_client import supabase


BUCKET = "patient-photos"
PUBLIC_PREFIX = "/storage/v1/object/public/"


def _extract_storage_filename(public_url: str) -> str | None:
    """
    public_url example:
      https://xxxx.supabase.co/storage/v1/object/public/patient-photos/<filename>
    """
    if not public_url:
        return None
    parsed = urlparse(public_url)
    if not parsed.path.startswith(PUBLIC_PREFIX):
        return None
    # remove bucket path
    # /storage/v1/object/public/patient-photos/<filename>
    marker = f"/storage/v1/object/public/{BUCKET}/"
    if marker in parsed.path:
        return parsed.path.split(marker, 1)[1]
    return None


async def upload_patient_photo_to_storage(file_bytes: bytes, original_filename: str, content_type: str | None) -> str:
    file_id = str(uuid4())
    ext = Path(original_filename).suffix or ".jpg"
    file_name = f"{file_id}{ext}"

    res = supabase.storage.from_(BUCKET).upload(
        path=file_name,
        file=file_bytes,
        file_options={"content-type": content_type or "image/jpeg"},
    )

    res_dict = res if isinstance(res, dict) else getattr(res, "__dict__", {})
    if res_dict.get("status_code", 200) >= 400:
        msg = res_dict.get("message", "Unknown error")
        raise RuntimeError(f"Storage upload failed: {msg}")

    return supabase.storage.from_(BUCKET).get_public_url(file_name)


async def remove_patient_photo_from_storage(public_url: str) -> None:
    file_name = _extract_storage_filename(public_url)
    if not file_name:
        return
    supabase.storage.from_(BUCKET).remove([file_name])
