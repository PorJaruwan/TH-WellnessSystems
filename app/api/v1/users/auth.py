import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header, Depends

# 🔐 โหลด Firebase Admin SDK Key
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    id_token = authorization.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Token verification failed")
