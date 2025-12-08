# # save as get_firebase_token.py (แทนของเดิมได้เลย)
# import os, sys, json, argparse, requests

# # from dotenv import load_dotenv
# # load_dotenv()


# FIREBASE_API_KEY = os.getenv("FIREBASE_WEB_API_KEY") or "AIzaSyBELMRrMMO-9Q0CmZKwRpyfpm3ny9Yn2eg"  # <-- อัปเดตให้ตรงจาก Console!

# def _print_json(d): print(json.dumps(d, ensure_ascii=False, indent=2))

# def login(email: str, password: str):
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
#     payload = {"email": email, "password": password, "returnSecureToken": True}
#     r = requests.post(url, json=payload, timeout=20)
#     if r.status_code != 200:
#         raise SystemExit(f"HTTP {r.status_code} {r.text}")
#     return r.json()

# def signup(email: str, password: str):
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
#     payload = {"email": email, "password": password, "returnSecureToken": True}
#     r = requests.post(url, json=payload, timeout=20)
#     if r.status_code != 200:
#         raise SystemExit(f"HTTP {r.status_code} {r.text}")
#     return r.json()

# def main():
#     ap = argparse.ArgumentParser()
#     sub = ap.add_subparsers(dest="cmd", required=True)

#     p1 = sub.add_parser("login")
#     p1.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"))
#     p1.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"))

#     p2 = sub.add_parser("signup")
#     p2.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"))
#     p2.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"))

#     args = ap.parse_args()

#     if args.cmd == "login":
#         if not args.email or not args.password:
#             raise SystemExit("ต้องระบุ --email และ --password หรือกำหนดใน ENV")
#         data = login(args.email, args.password)
#         print("✅ Login สำเร็จ — Firebase ID Token:")
#         _print_json(data)

#     elif args.cmd == "signup":
#         if not args.email or not args.password:
#             raise SystemExit("ต้องระบุ --email และ --password หรือกำหนดใน ENV")
#         data = signup(args.email, args.password)
#         print("✅ Sign up สำเร็จ")
#         _print_json(data)

# if __name__ == "__main__":
#     main()




# # import os
# # import sys
# # import json
# # import argparse
# # import pyrebase

# # # ===============================
# # #  Firebase Auth Helper (Pyrebase)
# # # ===============================

# # # ✅ Firebase config (จาก JS config ที่คุณให้มา)
# # firebase_config = {
# #     "apiKey": "AIzaSyBELMRrMMO-9Q0CmZKwRpyfpm3ny9Yn2eg",
# #     "authDomain": "welness-c9ce4.firebaseapp.com",
# #     "projectId": "welness-c9ce4",
# #     "storageBucket": "welness-c9ce4.firebasestorage.app",
# #     "messagingSenderId": "67051456566",
# #     "appId": "1:67051456566:web:4f92f299a85ef505837097",
# #     "measurementId": "G-37Y8BSQEX5",
# #     "databaseURL": ""  # ไม่ใช้ Realtime DB ก็เว้นได้
# # }


# # firebase = pyrebase.initialize_app(firebase_config)
# # auth = firebase.auth()

# # # -------------------------------
# # # Utility
# # # -------------------------------
# # def _print_json(data):
# #     print(json.dumps(data, ensure_ascii=False, indent=2))

# # # -------------------------------
# # # Core functions
# # # -------------------------------
# # def signup(email: str, password: str, *, send_verification: bool = True):
# #     """สมัครผู้ใช้ใหม่ด้วย Email/Password
# #     - สร้าง user
# #     - ลงชื่อเข้าใช้เพื่อรับ idToken
# #     - (ตัวเลือก) ส่งอีเมลยืนยันตัวตน
# #     คืนค่า: dict ที่มี localId, email, idToken
# #     """
# #     # 1) Create user
# #     created = auth.create_user_with_email_and_password(email, password)

# #     # 2) Sign in to obtain idToken
# #     signed_in = auth.sign_in_with_email_and_password(email, password)
# #     id_token = signed_in.get("idToken")

# #     # 3) Optional: send verification email
# #     if send_verification and id_token:
# #         try:
# #             auth.send_email_verification(id_token)
# #             verification_sent = True
# #         except Exception:
# #             verification_sent = False
# #     else:
# #         verification_sent = False

# #     return {
# #         "localId": created.get("localId"),
# #         "email": email,
# #         "idToken": id_token,
# #         "verificationEmailSent": verification_sent,
# #     }

# # def login(email: str, password: str):
# #     """ลงชื่อเข้าใช้และพิมพ์ Firebase ID Token"""
# #     user = auth.sign_in_with_email_and_password(email, password)
# #     return {
# #         "email": email,
# #         "idToken": user.get("idToken"),
# #         "refreshToken": user.get("refreshToken"),
# #         "expiresIn": user.get("expiresIn"),
# #     }

# # # -------------------------------
# # # CLI
# # # -------------------------------
# # def main():
# #     parser = argparse.ArgumentParser(
# #         description="Firebase Email/Password Auth helper (Pyrebase)",
# #         formatter_class=argparse.ArgumentDefaultsHelpFormatter
# #     )
# #     sub = parser.add_subparsers(dest="command", required=True)

# #     # signup command
# #     p_signup = sub.add_parser("signup", help="สมัครผู้ใช้ใหม่ (Sign up)")
# #     p_signup.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"), help="อีเมลของผู้ใช้ใหม่ (หากไม่ใส่จะอ่านจาก env FIREBASE_EMAIL)")
# #     p_signup.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"), help="รหัสผ่านของผู้ใช้ใหม่ (หรือ env FIREBASE_PASSWORD)")
# #     p_signup.add_argument("--no-verify", action="store_true", help="ไม่ส่งอีเมลยืนยันตัวตน")

# #     # login command
# #     p_login = sub.add_parser("login", help="ลงชื่อเข้าใช้ (Sign in)")
# #     p_login.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"), help="อีเมลสำหรับลงชื่อเข้าใช้ (หรือ env FIREBASE_EMAIL)")
# #     p_login.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"), help="รหัสผ่านสำหรับลงชื่อเข้าใช้ (หรือ env FIREBASE_PASSWORD)")

# #     args = parser.parse_args()

# #     if args.command == "signup":
# #         if not args.email or not args.password:
# #             print("❌ กรุณาระบุ --email และ --password หรือกำหนดใน ENV: FIREBASE_EMAIL/FIREBASE_PASSWORD")
# #             sys.exit(1)
# #         try:
# #             data = signup(args.email, args.password, send_verification=not args.no_verify)
# #             print("✅ Sign up สำเร็จ")
# #             _print_json(data)
# #         except Exception as e:
# #             print("❌ Sign up ล้มเหลว:", e)
# #             sys.exit(2)

# #     elif args.command == "login":
# #         if not args.email or not args.password:
# #             print("❌ กรุณาระบุ --email และ --password หรือกำหนดใน ENV: FIREBASE_EMAIL/FIREBASE_PASSWORD")
# #             sys.exit(1)
# #         try:
# #             data = login(args.email, args.password)
# #             print("✅ Login สำเร็จ — Firebase ID Token (ใช้กับ API):")
# #             _print_json(data)
# #         except Exception as e:
# #             print("❌ Login ล้มเหลว:", e)
# #             sys.exit(2)

# # if __name__ == "__main__":
# #     main()