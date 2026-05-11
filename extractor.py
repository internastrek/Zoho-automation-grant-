import os
import json
import re
from datetime import datetime, timedelta
from groq import Groq
from schemas import GrantDetails


TYPE_MAPPING = {
    "applications": "Applications",
    "awards": "Awards",
    "events": "Events",
    "other opportunities": "Other Opportunities",
    "accelerator": "Accelerators",
    "accelerators": "Accelerators",
    "pilot": "Pilot",
    "grants": "Grants",
    "investments": "Investments"
}


def extract_grant_details(raw_text: str, url: str):

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
You are an expert grant analyst.

Extract the following details from the grant information below.

Type of opportunity must be one of:
applications, awards, events, other opportunities, accelerators, pilot, grants, investments.

For submission_deadline, return the date in this format: "Month Day, Year" e.g. "May 11, 2026".
If only month and year are available, return "Month 1, Year" e.g. "May 1, 2026".
If no year is mentioned, assume 2026.

Return ONLY valid JSON in this exact format:

{{
  "oppurtunity_name": "",
  "type_of_oppurtunity": "",
  "amount": "",
  "submission_deadline": "",
  "description": ""
}}

Grant Information:
{raw_text[:8000]}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    response_text = completion.choices[0].message.content.strip()

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON found in model response.")

    data = json.loads(match.group())

    submission_deadline = data.get("submission_deadline", "")
    first_draft_date = ""

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

    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(submission_deadline.strip(), fmt)
            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=2026)
            break
        except:
            continue

    if parsed_date:
        first_draft = parsed_date - timedelta(days=7)
        first_draft_date = first_draft.strftime("%B %d, %Y")
    else:
        first_draft_date = "Unable to auto-calculate"

    raw_type = data.get("type_of_oppurtunity", "").lower().strip()
    mapped_type = TYPE_MAPPING.get(raw_type, "Other Opportunities")

    final_data = {
        "oppurtunity_name": data.get("oppurtunity_name", ""),
        "website": url,
        "type_of_oppurtunity": mapped_type,
        "amount": data.get("amount", ""),
        "submission_deadline": submission_deadline,
        "first_draft_date": first_draft_date,
        "description": data.get("description", "")
    }

    return GrantDetails(**final_data)