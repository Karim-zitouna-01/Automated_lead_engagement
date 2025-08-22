from typing import List, Dict
from Lead_Identification.detection.agent_google.agent import google_agent
from Lead_Identification.detection.agent_tavily.backend_1_enrichment.lead_enrichment_module import get_enriched_leads_report
# Uncomment the following line if you have a LinkedIn agent implemented
# from detection.agent_linkedin import linkedin_agent  # Uncomment if exists
from Lead_Identification.common.llms import call_gemini_flash,call_mistral
from concurrent.futures import ThreadPoolExecutor, as_completed


import json

def detection_agent(icp: Dict) -> List[Dict]:
    """
    Runs Tavely and Google agents in parallel, aggregates results,
    and uses an LLM to detect duplicate/conflicting leads.
    """

    all_leads = []

    with ThreadPoolExecutor() as executor:
        # Submit both tasks at the same time
        futures = {
            executor.submit(get_enriched_leads_report, icp): "Tavely",
            executor.submit(google_agent, icp): "Google"
        }

        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                leads = future.result()
                print(f"[✅] {agent_name} agent returned {len(leads)} leads")
                all_leads.extend(leads)
            except Exception as e:
                print(f"[❌] {agent_name} agent failed: {e}")

    print(f"=== 🧹 Total leads collected: {len(all_leads)} ===")

    # Call LLM to analyze for duplicates
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
        response = call_mistral(llm_input, max_tokens=100000, temperature=0.1)
        print("llm response: \n", response)
        return json.loads(response)
    except Exception as e:
        print(f"[❌] LLM analysis failed: {e}")
        return leads
 