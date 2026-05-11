import requests
import re
import json
from datetime import datetime
from bigin_auth import get_access_token

def clean_amount(amount_str):
    amount_str = str(amount_str).lower().replace(",", "")
    match = re.search(r'[\d.]+', amount_str)
    if not match:
        return 0.0
    value = float(match.group())
    if "million" in amount_str:
        value *= 1_000_000
    elif "thousand" in amount_str or "k" in amount_str:
        value *= 1_000
    return value

def clean_date(date_str):
    if not date_str or "unable" in date_str.lower() or "n/a" in date_str.lower():
        return None
    try:
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str).strip()

        date_formats = [
            "%B %d, %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%d %b %Y",
            "%B %Y",
            "%b %Y",
            "%d %B",
            "%B %d",
        ]

        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if parsed.year == 1900:
                    parsed = parsed.replace(year=2026)
                return parsed.strftime("%Y-%m-%d")
            except:
                continue
        return None
    except:
        return None

def push_to_bigin(grant_data: dict):

    access_token = get_access_token()

    url = "https://www.zohoapis.in/bigin/v2/Pipelines"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "data": [
            {
                "Deal_Name": grant_data["oppurtunity_name"],
                "Layout": {"id": "645408000000471242"},
                "Sub_Pipeline": "Funding Applications Standard",
                "Stage": "Applications Identified",
                "Website": grant_data["website"],
                "Amount": clean_amount(grant_data["amount"]) or None,
                "Type_of_Opportunity": grant_data["type_of_oppurtunity"],
                "First_Draft_date": clean_date(grant_data["first_draft_date"]),
                "Submission_Date": clean_date(grant_data["submission_deadline"]) or "2026-12-31",
                "Description": grant_data["description"],
                "Tag": [{"name": "Automated"}]
            }
        ]
    }

    print("PAYLOAD BEING SENT:", json.dumps(payload, indent=2))

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)

    return response.json()