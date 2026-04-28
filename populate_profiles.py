import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

URL = f"https://{os.getenv('SUPABASE_PROJECT_ID')}.supabase.co/rest/v1"
HEADERS = {
    "apikey": os.getenv('SUPABASE_SECRET_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SECRET_KEY')}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

users = [
    {"email": "test@gmail.com", "uid": "8520e376-beb2-42ed-a484-366d0cf824dc", "role": "parent", "name": "Parent User"},
    {"email": "ravirajraibagkar@gmail.com", "uid": "132515f2-7148-48a8-8082-951b76b28f44", "role": "parent", "name": "Raviraj Admin"},
    {"email": "child@test.com", "uid": "2ef6c6e1-fd44-406b-8da6-9e8713e4af95", "role": "child", "name": "Student User"}
]

print("--- Populating public.profiles ---")
parent_profile_id = None
child_user_id = None

for u in users:
    data = {
        "user_id": u["uid"],
        "name": u["name"],
        "role": u["role"]
    }
    res = requests.post(f"{URL}/profiles", headers=HEADERS, json=data)
    if res.status_code in [200, 201]:
        profile = res.json()[0]
        print(f"[CREATED] Profile for {u['email']} (ID: {profile['id']})")
        if u["role"] == "parent" and not parent_profile_id:
            parent_profile_id = profile["id"]
        if u["role"] == "child":
            child_user_id = u["uid"]
    else:
        print(f"[ERROR] Failed to create profile for {u['email']}: {res.text}")

if parent_profile_id and child_user_id:
    print("\n--- Linking Child to Parent ---")
    link_data = {
        "parent_id": parent_profile_id,
        "child_user_id": child_user_id,
        "name": "Student User",
        "age": 10
    }
    res = requests.post(f"{URL}/children", headers=HEADERS, json=link_data)
    if res.status_code in [200, 201]:
        print("[LINKED] Student User linked to Parent User in public.children table")
    else:
        print(f"[ERROR] Linking failed: {res.text}")
