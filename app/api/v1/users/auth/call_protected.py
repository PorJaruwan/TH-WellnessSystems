# import subprocess, sys, json, requests, argparse, shlex, os
# from pathlib import Path

# # optional clipboard
# try:
#     import pyperclip
# except ImportError:
#     pyperclip = None

# # UTF-8 on Windows
# try:
#     if not sys.stdout.encoding or "utf" not in sys.stdout.encoding.lower():
#         sys.stdout.reconfigure(encoding="utf-8")
# except Exception:
#     os.environ.setdefault("PYTHONIOENCODING","utf-8")
#     os.environ.setdefault("PYTHONUTF8","1")

# # load .env
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except Exception:
#     pass

# BASE_URL = "http://127.0.0.1:8000"
# TOKEN_SCRIPT = "get_firebase_token.py"
# PYTHON_EXEC  = sys.executable
# DEFAULT_ENDPOINT = "/api/v1/auth_firebase/me"

# def copy_to_clipboard(text: str):
#     if pyperclip:
#         try:
#             pyperclip.copy(text)
#             print("📋 Token copied to clipboard.")
#             return
#         except Exception:
#             pass
#     # fallbacks
#     try:
#         if sys.platform == "win32":
#             subprocess.run("clip", input=text, text=True, check=True)
#         elif sys.platform == "darwin":
#             subprocess.run("pbcopy", input=text, text=True, check=True)
#         else:
#             subprocess.run("xclip -selection clipboard", input=text, text=True, shell=True, check=True)
#         print("📋 Token copied to clipboard.")
#     except Exception:
#         print("ℹ️  Could not copy to clipboard automatically.")

# def get_token(email: str, password: str, api_key: str | None):
#     # 1) try helper script (preferred)
#     env = os.environ.copy()
#     env.setdefault("PYTHONIOENCODING","utf-8")
#     env.setdefault("PYTHONUTF8","1")
#     try:
#         proc = subprocess.run(
#             [PYTHON_EXEC, TOKEN_SCRIPT, "login", "--email", email, "--password", password],
#             capture_output=True, text=True, check=True, env=env
#         )
#         out = proc.stdout.strip()
#         # last JSON object
#         start, end = out.find("{"), out.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             data = json.loads(out[start:end+1])
#             tok = data.get("idToken")
#             if tok:
#                 return tok
#     except subprocess.CalledProcessError as e:
#         print("⚠️  get_firebase_token.py failed; will try REST fallback.")

#     # 2) REST fallback (requires WEB API KEY)
#     if not api_key:
#         raise SystemExit("ไม่พบ FIREBASE_WEB_API_KEY สำหรับ REST fallback และเรียกสคริปต์ล้มเหลว")
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
#     r = requests.post(url, json={"email":email,"password":password,"returnSecureToken":True}, timeout=20)
#     if r.status_code != 200:
#         raise SystemExit(f"Login failed (HTTP {r.status_code}): {r.text}")
#     return r.json()["idToken"]

# def main():
#     ap = argparse.ArgumentParser(description="Call protected API with Firebase token")
#     ap.add_argument("endpoint", nargs="?", default=DEFAULT_ENDPOINT, help="API endpoint path (default: /api/v1/auth_firebase/me)")
#     ap.add_argument("--method", default="GET", choices=["GET","POST","PUT","PATCH","DELETE"])
#     ap.add_argument("--data", help="JSON string body for POST/PUT/PATCH")
#     ap.add_argument("--base-url", default=BASE_URL)
#     ap.add_argument("--email", default=os.getenv("FIREBASE_EMAIL"))
#     ap.add_argument("--password", default=os.getenv("FIREBASE_PASSWORD"))
#     ap.add_argument("--api-key", default=os.getenv("FIREBASE_WEB_API_KEY"))
#     args = ap.parse_args()

#     if not args.email or not args.password:
#         raise SystemExit("❌ โปรดกำหนด --email และ --password หรือใส่ FIREBASE_EMAIL/FIREBASE_PASSWORD ใน .env")

#     token = get_token(args.email, args.password, args.api_key)
#     bearer = f"Bearer {token}"
#     copy_to_clipboard(bearer)

#     url = args.base_url.rstrip("/") + (args.endpoint if args.endpoint.startswith("/") else f"/{args.endpoint}")
#     headers = {"Authorization": bearer}

#     # show curl
#     curl = f'curl -i {shlex.quote(url)} -H "Authorization: {bearer}"'
#     if args.method != "GET" and args.data:
#         curl = f'curl -i -X {args.method} {shlex.quote(url)} -H "Authorization: {bearer}" -H "Content-Type: application/json" -d {shlex.quote(args.data)}'
#     print("\n=== Equivalent curl ===\n" + curl + "\n")

#     # request
#     json_body = None
#     if args.data:
#         json_body = json.loads(args.data)
#     resp = requests.request(args.method, url, headers=headers, json=json_body, timeout=30)
#     print(f"HTTP {resp.status_code}")
#     try:
#         print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
#     except Exception:
#         print(resp.text)

# if __name__ == "__main__":
#     main()
