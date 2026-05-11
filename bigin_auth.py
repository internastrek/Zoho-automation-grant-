import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_access_token():
    url = "https://accounts.zoho.in/oauth/v2/token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": os.getenv("ZOHO_CLIENT_ID"),
        "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
        "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN")
    }

    response = requests.post(url, data=payload)
    print("Auth response:", response.text)  # add this line

    if response.status_code != 200:
        raise Exception(f"Token error: {response.text}")

    return response.json()["access_token"]
if __name__ == "__main__":
    print(get_access_token())