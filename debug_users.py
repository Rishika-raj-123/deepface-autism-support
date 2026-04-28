import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

URL = f"https://{os.getenv('SUPABASE_PROJECT_ID')}.supabase.co/rest/v1"
HEADERS = {
    "apikey": os.getenv('SUPABASE_SECRET_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SECRET_KEY')}"
}

res = requests.get(f"{URL}/custom_users", headers=HEADERS)
print(res.text)
