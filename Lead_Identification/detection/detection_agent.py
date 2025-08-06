from typing import List, Dict
from Lead_Identification.detection.agent_google.agent import google_agent
from Lead_Identification.detection.agent_tavily.backend_1_enrichment.lead_enrichment_module import get_enriched_leads_report
# Uncomment the following line if you have a LinkedIn agent implemented
# from detection.agent_linkedin import linkedin_agent  # Uncomment if exists
from Lead_Identification.common.llms import call_gemini_flash,call_mistral


import json

def detection_agent(icp: Dict) -> List[Dict]:
    """
    Calls multiple lead-generating agents, aggregates their results,
    and uses an LLM to detect duplicate/conflicting leads.
    """

    all_leads = []

    print("=== 📊 launching tavely agent ===")
    
    
    tavely_leads = get_enriched_leads_report(icp)
    print(f"tavely leads : {tavely_leads}")
    
    print(f"[✅] Tavely agent returned {len(tavely_leads)} leads")
    all_leads.extend(tavely_leads)

    print("=== 🔍 Launching Google Agent ===")
    google_leads = google_agent(icp)
    print(f"[✅] Google agent returned {len(google_leads)} leads")
    all_leads.extend(google_leads)



    # Optional: add other agents here
    # print("=== 🧠 Launching LinkedIn Agent ===")
    # linkedin_leads = linkedin_agent(icp)
    # print(f"[✅] LinkedIn agent returned {len(linkedin_leads)} leads")
    # all_leads.extend(linkedin_leads)

    print(f"=== 🧹 Total leads collected: {len(all_leads)} ===")

    # Call LLM to analyze for duplicates or similar names
    final_leads = analyze_and_detect_duplicates(all_leads)

    return final_leads


def analyze_and_detect_duplicates(leads: List[Dict]) -> List[Dict]:
    """
    Uses LLM to detect potential duplicates or conflicting entries.
    """
    prompt = f"""
You are a lead deduplication assistant.

I will give you a list of leads in JSON format. Each lead contains a name, company, role, and reason_for_match.

Your task:
- Detect if there are leads that seem to refer to the same person or company, even if names are slightly different (e.g. "Ahmed Zitouna" vs "A. Zitouna")
- Merge such leads if possible


Return only the final cleaned list of JSONs (without any additional text or explanation) in the following format:
[
  {{
    - company_name: str
    - summary: str
    - description: str
    - reason_for_match: str or null
    - key_personal: list of json (can be empty)
    - relevant_urls: list of str (can be empty)
  }},
  ...
]
the key personal field should be a list of json objects with the following fields:
- name: str
- role: str (can be empty)
- linkedin_url: str (can be empty)
"""

    try:
        leads_str = json.dumps(leads, indent=2)
        llm_input = f"{prompt}\n\nLeads:\n{leads_str}"
        response = call_mistral(llm_input, max_tokens=10000, temperature=0.2)
        print("llm response: \n", response)
        return json.loads(response)
    except Exception as e:
        print(f"[❌] LLM analysis failed: {e}")
        return leads
 