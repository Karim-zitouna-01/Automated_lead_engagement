import os
import json
from typing import List, Dict, Any, Optional, TypedDict
from dotenv import load_dotenv
import google.generativeai as genai
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class KeyPersonnel(TypedDict):
    name: str
    title: str
    linkedin_profile: Optional[str]
    recent_activity: Optional[str]
    points_of_interest: Optional[List[str]]
    potential_pain_points: Optional[List[str]]

def get_enriched_personnel_profiles(
    personnel_list: List[Dict[str, Any]],
    company_name: str,
    icp: Dict[str, Any]
) -> List[KeyPersonnel]:
    enriched_personnel_list: List[KeyPersonnel] = []
    for person in personnel_list:
        name = person.get("name")
        if not name:
            continue
        enriched: KeyPersonnel = {
            "name": name,
            "title": person.get("title"),
            "linkedin_profile": person.get("linkedin_profile"),
            "recent_activity": "No specific recent activity found.",
            "points_of_interest": [],
            "potential_pain_points": []
        }
        queries = [
            f'recent articles or interviews by "{name}" "{company_name}"',
            f'"{name}" "{company_name}" professional focus priorities',
            f'linkedin posts by "{name}" on challenges in the {icp.get("industry", {}).get("tier1_core_focus",[None])[0]} sector'
        ]
        context = ""
        for q in queries:
            resp = tavily_client.search(query=q, search_depth="advanced", max_results=2)
            context += "\n".join([res.get("content","") for res in resp.get("results", [])]) + "\n"
        if context.strip():
            prompt = f"""
Based on the following information about {name}, {enriched['title']} at {company_name}, and ICP pain points: {', '.join(icp.get('pain_points',[]))}:

Research context:
---
{context}
---

Please return a JSON object with:
{{
  "recent_activity": "...",
  "points_of_interest": ["...", "..."],
  "potential_pain_points": ["...", "..."]
}}
"""
            resp = llm.invoke(prompt)
            text = resp.content.strip()
            js_start = text.find("{")
            js_end = text.rfind("}")
            if js_start != -1 and js_end != -1:
                try:
                    parsed = json.loads(text[js_start:js_end+1])
                    enriched.update(parsed)
                except json.JSONDecodeError:
                    pass
        enriched_personnel_list.append(enriched)
    return enriched_personnel_list

# if __name__ == "__main__":
#     personnel_list = [
#         {"name": "Thierry Millet", "title": "CEO, Orange Tunisie", "linkedin_profile": None},
#         {"name": "Siwar Farhat", "title": "Former Director Sofrecom Tunisia", "linkedin_profile": None}
#     ]
#     company_name = "Orange Tunisie"
#     icp = {
#         "industry": {"tier1_core_focus": ["digital transformation", "telecom services"]},
#         "pain_points": ["digital adoption among SMEs", "cybersecurity services uptake", "start-up acceleration"]
#     }
#     enriched = get_enriched_personnel_profiles(personnel_list, company_name, icp)
#     print(json.dumps(enriched, indent=2, ensure_ascii=False))