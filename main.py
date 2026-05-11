from bigin_client import push_to_bigin
from dotenv import load_dotenv
load_dotenv()

from scraper import scrape_website
from extractor import extract_grant_details

url = input("Enter Grant URL: ")

raw_text = scrape_website(url)
grant_data = extract_grant_details(raw_text, url)

print(grant_data.model_dump_json(indent=4))
push_to_bigin(grant_data.model_dump())