import requests
import os
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')

PROJECT_ID = os.getenv('SUPABASE_PROJECT_ID')
AUTH_URL = f"https://{PROJECT_ID}.supabase.co/auth/v1"
REST_URL = f"https://{PROJECT_ID}.supabase.co/rest/v1"
ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')

HEADERS_ANON = {"apikey": ANON_KEY, "Content-Type": "application/json"}
HEADERS_SECRET = {"apikey": SECRET_KEY, "Authorization": f"Bearer {SECRET_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

def create_user(email, password, role, name):
    print(f"--- Creating {role}: {email} ---")
    
    # 1. Sign up user in Auth
    signup_res = requests.post(f"{AUTH_URL}/signup", headers=HEADERS_ANON, json={"email": email, "password": password})
    if signup_res.status_code == 200:
        uid = signup_res.json().get('id')
        print(f"[OK] Auth user created (UID: {uid})")
    elif signup_res.status_code == 400 and "already registered" in signup_res.text:
        # If already exists, we'll try to sign in to get the UID.
        login_res = requests.post(f"{AUTH_URL}/token?grant_type=password", headers=HEADERS_ANON, json={"email": email, "password": password})
        if login_res.status_code == 200:
            uid = login_res.json()['user']['id']
            print(f"[INFO] User already exists, using existing UID: {uid}")
        else:
            # Maybe it exists but with different password? We can't know. 
            # We'll just assume the UID is what we need if we could find it.
            print(f"[ERR] User exists but login failed: {login_res.text}")
            return None
    else:
        print(f"[ERR] Signup failed: {signup_res.text}")
        return None

    # 2. Create Profile
    profile_data = {"user_id": uid, "name": name, "role": role}
    prof_res = requests.post(f"{REST_URL}/profiles", headers=HEADERS_SECRET, json=profile_data)
    if prof_res.status_code in [200, 201]:
        profile = prof_res.json()[0]
        print(f"[OK] Profile created (ID: {profile['id']})")
        return {"uid": uid, "profile_id": profile['id']}
    elif prof_res.status_code == 409 or "already exists" in prof_res.text:
        prof_res = requests.get(f"{REST_URL}/profiles?user_id=eq.{uid}", headers=HEADERS_SECRET)
        data = prof_res.json()
        if data:
            profile = data[0]
            print(f"[INFO] Profile already exists (ID: {profile['id']})")
            return {"uid": uid, "profile_id": profile['id']}
        return None
    else:
        print(f"[ERR] Profile creation failed: {prof_res.text}")
        return None

# --- Main Execution ---
password = "password123"

# Create Parent
parent = create_user("parent@example.com", password, "parent", "Demo Parent")

# Create Child
child = create_user("child@example.com", password, "child", "Demo Child")

if parent and child:
    # Link Child to Parent
    print("\n--- Linking Child to Parent ---")
    link_data = {
        "parent_id": parent['profile_id'],
        "child_user_id": child['uid'],
        "name": "Demo Child",
        "age": 10
    }
    link_res = requests.post(f"{REST_URL}/children", headers=HEADERS_SECRET, json=link_data)
    if link_res.status_code in [200, 201, 409] or "already exists" in link_res.text:
        print("[OK] Link established in children table!")
        print("\n🚀 DONE! USE THESE FOR TESTING:")
        print(f"Parent: parent@example.com / Password: {password}")
        print(f"Child:  child@example.com  / Password: {password}")
    else:
        print(f"[ERR] Linking failed: {link_res.text}")
