import requests
from dotenv import load_dotenv
from bigin_auth import get_access_token

load_dotenv()

def get_layouts():
    access_token = get_access_token()
    url = "https://www.zohoapis.in/bigin/v1/settings/layouts?module=Deals"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(response.text)

get_layouts()