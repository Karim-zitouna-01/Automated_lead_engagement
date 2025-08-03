# Lead_Identification/detection/agent_google/agent.py

import json
from typing import List, Dict

from detection.agent_google.utils import generate_search_queries, search_duckduckgo, crawl_and_clean, summarize_page

def google_agent(icp: Dict) -> List[Dict]:

    leads = []
    print("generating search queries based on ICP...\n")
    queries = generate_search_queries(icp)
    print(f"Generated {len(queries)} queries based on ICP")
    print(queries)
    
    for query in queries:
        print(f"[🔍] Searching: {query}")
        urls = search_duckduckgo(query, top_k=2)
        
        for url in urls:
            print(f"[🌐] Crawling URL: {url}")
            raw_content = crawl_and_clean(url)
            summary_json = summarize_page(raw_content, icp)
            print(f"[📝] Summary for {url}:\n {summary_json}\n")

            try:
                summary = json.loads(summary_json)
                if summary.get("reason_for_match"):
                    leads.append(summary)
            except Exception as e:
                print(f"[⚠️] Could not parse summary: {e}")
                print(f"[⚠️] Summary content: {summary_json}")
                continue
            
            
    return leads


