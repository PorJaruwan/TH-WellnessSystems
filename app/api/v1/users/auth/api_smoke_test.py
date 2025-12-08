# """
# API Smoke Test for Wellness FastAPI
# Run examples:
#   # PowerShell / CMD
#   python api_smoke_test.py --base-url http://127.0.0.1:8000 --public-path /docs --protected-path /api/v1/users/me --use-login 1

#   # Git Bash (ปิด path conversion)
#   MSYS2_ARG_CONV_EXCL="*" python api_smoke_test.py --base-url http://127.0.0.1:8000 --public-path /docs --protected-path /api/v1/users/me --use-login 1
# """
# import os, sys, json, subprocess, argparse, requests, shlex  # ensure os, sys, shlex imported
# from urllib.parse import urljoin

# from dotenv import load_dotenv
# load_dotenv()  # <-- ให้ .env กลายเป็น environment ของโปรเซสนี้


# def normalize_web_path(p: str) -> str:
#     """
#     ป้องกัน Git Bash แปลง '/docs' -> 'C:/Program Files/Git/docs'
#     บังคับให้เป็น path แบบเว็บที่ขึ้นต้นด้วย '/'
#     """
#     if not p:
#         return "/"
#     # ถ้าเผลอได้แบบ 'C:/Program Files/Git/docs' หรือมี backslash ให้ force เป็น '/docs'
#     lowered = p.replace("\\", "/")
#     if ":/Program Files/Git/" in lowered:
#         return "/" + lowered.split(":/Program Files/Git/")[-1]
#     # ถ้าไม่มี prefix '/' ให้เติม
#     if not lowered.startswith("/"):
#         lowered = "/" + lowered
#     return lowered

# def find_script(default_name: str, override: str | None) -> str:
#     if override:
#         return override
#     candidates = [
#         default_name,                          # ./get_firebase_token.py
#         os.path.join("scripts", default_name),
#         os.path.join("tools", default_name),
#         os.path.join("app", default_name),
#     ]
#     for c in candidates:
#         if os.path.isfile(c):
#             return c
#     # สุดท้ายคืนชื่อเดิมให้ subprocess ลองรัน (อาจอยู่ใน PATH/โฟลเดอร์อื่น)
#     return default_name

# def get_token_via_login(py_exec: str, script_path: str, extra_args: str = "") -> str:
#     import re, shlex

#     args_list = ["login"]
#     if extra_args:
#         args_list += shlex.split(extra_args)

#     # ส่ง ENV และบังคับ stdout เป็น UTF‑8 กัน error อีโมจิ/ภาษาไทยบน Windows
#     env = os.environ.copy()
#     env.setdefault("PYTHONIOENCODING", "utf-8")
#     env.setdefault("PYTHONUTF8", "1")

#     proc = subprocess.run(
#         [py_exec, script_path, *args_list],
#         check=True, capture_output=True, text=True,
#         env=env,
#     )

#     text = (proc.stdout or "").strip()

#     # 1) พยายามดึงก้อน JSON สุดท้าย
#     start, end = text.find("{"), text.rfind("}")
#     token = None
#     if start != -1 and end != -1 and end > start:
#         try:
#             data = json.loads(text[start:end+1])
#             token = data.get("idToken")
#         except Exception:
#             pass

#     # 2) fallback: regex หา "idToken":"..."
#     if not token:
#         m = re.search(r'"idToken"\s*:\s*"([^"]+)"', text)
#         if m:
#             token = m.group(1)

#     if not token:
#         raise RuntimeError("No idToken in login output")

#     return token


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of FastAPI server")
#     ap.add_argument("--public-path", default="/docs", help="Public path to test (e.g., /health or /docs)")
#     ap.add_argument("--protected-path", default="/api/v1/users/auth/me", help="Protected path that requires Bearer token")
#     ap.add_argument("--use-login", type=int, default=1, help="1=obtain token via login; 0=skip protected test")
#     #ap.add_argument("--python-exec", default="python", help="Python executable to invoke get_firebase_token.py")
#     ap.add_argument("--python-exec", default=sys.executable,help="Python executable to invoke get_firebase_token.py")
#     ap.add_argument("--token-script", default=None, help="Path to get_firebase_token.py if not in project root")
#     ap.add_argument("--token-script-args", default="", help="Extra args to pass to get_firebase_token.py (e.g. \"--email=... --password=...\")")
#     args = ap.parse_args()

#     base = args.base_url.rstrip("/")
#     public_path = normalize_web_path(args.public_path)
#     protected_path = normalize_web_path(args.protected_path)

#     # Public test
#     pub_url = base + public_path
#     print(f"== GET {pub_url}")
#     try:
#         r = requests.get(pub_url, timeout=10)
#         print(f"  -> {r.status_code}")
#     except Exception as e:
#         print(f"  ✗ Public path request failed: {e}")

#     # Protected test
#     if args.use_login:
#         script_path = find_script("get_firebase_token.py", args.token_script)
#         try:
#             token = get_token_via_login(args.python_exec, script_path)
#             print("  ✓ Obtained Firebase ID token (masked display)")
#             masked = token[:6] + "..." + token[-6:]
#             print(f"    token = {masked}")
#         except Exception as e:
#             print(f"  ✗ Failed to obtain token via login: {e}")
#             sys.exit(2)

#         prot_url = base + protected_path
#         print(f"== GET {prot_url} with Bearer token")
#         try:
#             r = requests.get(prot_url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
#             print(f"  -> {r.status_code}")
#             try:
#                 print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:2000])
#             except Exception:
#                 print(r.text[:2000])
#         except Exception as e:
#             print(f"  ✗ Protected path request failed: {e}")
#             sys.exit(3)

#     print("\n✅ Smoke test finished.")
#     return 0

# if __name__ == "__main__":
#     sys.exit(main())
