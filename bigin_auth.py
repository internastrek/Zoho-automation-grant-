import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_access_token():
    urls = [
        "https://accounts.zoho.com/oauth/v2/token",
        "https://accounts.zoho.in/oauth/v2/token"
    ]

    payload = {
        "grant_type": "refresh_token",
        "client_id": os.getenv("ZOHO_CLIENT_ID"),
        "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
        "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN")
    }

    for url in urls:
        try:
            print(f"Trying {url}...")
            response = requests.post(url, data=payload, timeout=10)
            print(f"Response: {response.status_code} - {response.text[:200]}")
            if response.status_code == 200:
                return response.json()["access_token"]
        except Exception as e:
            print(f"Failed with {url}: {e}")
            continue

    raise Exception("Could not connect to Zoho auth server")

if __name__ == "__main__":
    print(get_access_token())