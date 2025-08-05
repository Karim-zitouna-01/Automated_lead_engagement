import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict

from Automated_lead_engagement.server.models.lead import Lead,KeyPersonal



# Initialize Firebase
cred = credentials.Certificate("./secret/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to parse key_personals from raw strings
# def parse_key_personals(raw_list: List[str]) -> List[Dict[str, str]]:
#     parsed = []
#     for item in raw_list:
#         if "(" in item and item.endswith(")"):
#             name, role = item.rsplit("(", 1)
#             parsed.append({"name": name.strip(), "role": role.strip(") ").strip()})
#         else:
#             parsed.append({"name": item.strip(), "role": ""})
#     return parsed

# Main function to upload leads
def upload_leads_to_firestore(
    raw_leads: List[Dict],
    report_urls: Dict[str, str],
    service_id: str
):
    for lead in raw_leads:
        company_name = lead["company_name"]
        key_personals_raw = lead.get("key_personal", [])

        print("key personal raw:", key_personals_raw)
        parsed_key_personals = key_personals_raw

        print("parsed key personals:", parsed_key_personals)

        # Create Lead instance for validation
        lead_model = Lead(
            id="",  # Will not be used; Firestore auto-ID
            company_name=company_name,
            key_personals=[KeyPersonal(**kp) for kp in parsed_key_personals],
            report_url=report_urls.get(company_name, ""),
            qualification_url="",
            service_id=service_id
        )

        # Upload using Firestore auto-ID
        db.collection("Leads").add(lead_model.dict(exclude={"id"}))




# if __name__ == "__main__":
#     mock_detected_leads = [
#         {
#             "company_name": "OpenAI",
#             "key_personal": [
#                 "Sam Altman (CEO)",
#                 "Greg Brockman (President)",
#                 "Mira Murati"
#             ]
#         },
#         {
#             "company_name": "DeepMind",
#             "key_personal": [
#                 "Demis Hassabis (CEO)",
#                 "Mustafa Suleyman"
#             ]
#         }
#     ]

#     report_urls = {
#         "OpenAI": "https://example.com/reports/openai",
#         "DeepMind": "https://example.com/reports/deepmind"
#     }

#     service_id = "ai-consulting-service"

#     upload_leads_to_firestore(mock_detected_leads, report_urls, service_id)
#     print("✅ All leads uploaded.")
