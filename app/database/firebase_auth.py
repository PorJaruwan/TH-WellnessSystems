# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from firebase_admin import credentials, auth, initialize_app

# load_dotenv()

# # ---- Firebase Admin init (service account) ----
# cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
# if not cred_path:
#     raise Exception("FIREBASE_CREDENTIALS_PATH not set in .env")

# cred_file = Path(cred_path).expanduser().resolve()
# if not cred_file.exists():
#     raise FileNotFoundError(f"Firebase credentials file not found: {cred_file}")

# cred = credentials.Certificate(str(cred_file))
# try:
#     initialize_app(cred)   # กัน initialize ซ้ำตอน uvicorn --reload
# except ValueError:
#     pass

# # ---- ใช้ HTTPBearer (แนะนำ) ----
# bearer_scheme = HTTPBearer(auto_error=False)

# def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     """
#     ใช้กับ Swagger: กดปุ่ม Authorize (type: bearer) แล้ววาง 'ID Token' (ไม่ต้องพิมพ์คำว่า Bearer)
#     Swagger จะส่ง header 'Authorization: Bearer <token>' ให้อัตโนมัติ
#     """
#     if creds is None:
#         raise HTTPException(status_code=401, detail="Missing Authorization header")

#     token = creds.credentials  # ไม่ต้องตัดคำว่า 'Bearer '
#     try:
#         decoded = auth.verify_id_token(token)
#         return decoded
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")
###############################


# app/database/firebase_auth.py
import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import credentials, auth, initialize_app, _apps

load_dotenv()

# ---------------------------------------------------------
# Helpers: resolve credentials path with .env + smart fallbacks
# ---------------------------------------------------------

FILENAME = "firebase-adminsdk.json"


def _unique(seq: List[Path]) -> List[Path]:
    seen = set()
    out = []
    for p in seq:
        s = str(p)
        if s not in seen:
            out.append(p)
            seen.add(s)
    return out


def resolve_cred_path() -> Path:
    """Resolve Firebase service account JSON path.

    Priority:
      1) FIREBASE_CREDENTIALS_PATH from .env (supports absolute or relative)
      2) app/database/firebase-adminsdk.json (relative to project root)
      3) <this file's folder>/firebase-adminsdk.json

    Raises FileNotFoundError with all tried candidates.
    """
    cwd = Path.cwd()
    this_dir = Path(__file__).resolve().parent  # app/database
    project_root = this_dir.parent.parent  # assume root -> .../ (where 'app' lives)

    candidates: List[Path] = []

    env_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_absolute():
            candidates.append(p)
        else:
            # try resolve relative to cwd and project_root
            candidates.extend([
                cwd / p,
                project_root / p,
            ])

    # Conventional locations inside the repo
    candidates.extend([
        project_root / "app" / "database" / FILENAME,
        this_dir / FILENAME,
    ])

    tried = []
    for c in _unique(candidates):
        r = c.expanduser().resolve()
        tried.append(r)
        if r.exists():
            return r

    raise FileNotFoundError(
        "Firebase credentials file not found. Tried: \n - "
        + "\n - ".join(str(x) for x in tried)
        + f"\nCurrent working dir: {cwd}"
    )


# ---------------------------------------------------------
# Firebase Admin init (service account)
# ---------------------------------------------------------

cred_file = resolve_cred_path()
cred = credentials.Certificate(str(cred_file))

# Avoid double-initialize when using --reload
if not _apps:
    initialize_app(cred)

# ---------------------------------------------------------
# FastAPI dependency: HTTP Bearer + verify with Firebase Admin
# ---------------------------------------------------------

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Usage with Swagger UI:
      - Click **Authorize** (HTTP Bearer)
      - Paste your **Firebase ID Token** (do NOT type the word "Bearer")

    This dependency verifies the ID token via Firebase Admin.
    """
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = creds.credentials  # HTTPBearer already strips the scheme
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")
