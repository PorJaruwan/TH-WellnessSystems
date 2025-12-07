#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ดึง Firebase ID token แล้วพิมพ์เป็น "Bearer <token>" เพื่อวางในช่อง authorization ของ Swagger
แหล่งข้อมูล:
  - FIREBASE_WEB_API_KEY  (จาก Firebase Console → Project settings → Web API Key)
  - FIREBASE_EMAIL
  - FIREBASE_PASSWORD
อ่านจาก .env ได้อัตโนมัติ และรับผ่านอาร์กิวเมนต์ได้

ใช้งาน:
  python get_bearer.py
  python get_bearer.py --email you@example.com --password "your-pass"
  (ตั้งค่า .env: FIREBASE_WEB_API_KEY, FIREBASE_EMAIL, FIREBASE_PASSWORD)
"""

import os, sys, json, argparse
try:
    import requests
except ImportError:
    raise SystemExit("ต้องติดตั้ง requests ก่อน: pip install requests")
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None  # ใช้ได้แม้ไม่มี dotenv (แต่จะแปะจาก ENV เท่านั้น)

# บังคับ stdout เป็น UTF-8 บน Windows กันปัญหาอักขระ
try:
    if not sys.stdout.encoding or "utf" not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

load_dotenv()

def sign_in_with_password(api_key: str, email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=20)
    if r.status_code != 200:
        # โยนรายละเอียด error กลับไปให้เห็นชัดๆ
        raise SystemExit(f"Login ล้มเหลว (HTTP {r.status_code}): {r.text}")
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"))
    ap.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"))
    ap.add_argument("--api-key", default=os.getenv("FIREBASE_WEB_API_KEY"),
                    help="Firebase Web API Key (ถ้าไม่ใส่ จะอ่านจาก ENV FIREBASE_WEB_API_KEY)")
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("กรุณากำหนด --api-key หรือ ENV FIREBASE_WEB_API_KEY")
    if not args.email or not args.password:
        raise SystemExit("กรุณากำหนด --email และ --password หรือ ENV FIREBASE_EMAIL/FIREBASE_PASSWORD")

    data = sign_in_with_password(args.api_key, args.email, args.password)
    id_token = data.get("idToken")
    if not id_token:
        raise SystemExit(f"ไม่พบ idToken ในผลลัพธ์: {json.dumps(data, ensure_ascii=False)}")

    bearer = f"Bearer {id_token}"
    print("\n=== Bearer token (พร้อมวางใน Swagger) ===")
    print(bearer)

    # คัดลอกเข้าคลิปบอร์ดให้ด้วย หากมีไลบรารี pyperclip
    try:
        import pyperclip  # pip install pyperclip (ถ้าอยากให้คัดลอกอัตโนมัติ)
        pyperclip.copy(bearer)
        print("\nคัดลอกลงคลิปบอร์ดแล้ว ✅")
    except Exception:
        print("\n(ถ้าต้องการคัดลอกอัตโนมัติ: pip install pyperclip)")

    # แสดงอายุ token เผื่ออ้างอิง
    if "expiresIn" in data:
        print(f"\nexpiresIn: {data['expiresIn']} วินาที (~{int(data['expiresIn'])//60} นาที)")

if __name__ == "__main__":
    main()