import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

URL = f"https://{os.getenv('SUPABASE_PROJECT_ID')}.supabase.co/rest/v1"
HEADERS = {
    "apikey": os.getenv('SUPABASE_SECRET_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SECRET_KEY')}",
    "Content-Type": "application/json"
}

users = [
    {"email": "child@test.com", "uid": "2ef6c6e1-fd44-406b-8da6-9e8713e4af95"},
    {"email": "ravirajraibagkar@gmail.com", "uid": "132515f2-7148-48a8-8082-951b76b28f44"},
    {"email": "test@gmail.com", "uid": "8520e376-beb2-42ed-a484-366d0cf824dc"}
]

print("--- Checking Profiles ---")
for u in users:
    try:
        res = requests.get(f"{URL}/profiles?user_id=eq.{u['uid']}", headers=HEADERS)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"[OK] {u['email']} has profile: {data[0].get('name')} ({data[0].get('role')})")
        else:
            print(f"[MISSING] {u['email']} MISSING profile in public.profiles table")
    except Exception as e:
        print(f"[ERROR] {u['email']} check failed: {e}")

print("\n--- Checking Children Links ---")
for u in users:
    try:
        res = requests.get(f"{URL}/children?child_user_id=eq.{u['uid']}", headers=HEADERS)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"[LINKED] {u['email']} linked as child ID: {data[0].get('id')}")
        else:
            print(f"[NOT LINKED] {u['email']} not linked in public.children table")
    except Exception as e:
        print(f"[ERROR] {u['email']} child check failed: {e}")
