from typing import Dict, List
from detection.detection_agent import detection_agent
from enrichment.enrichir import enrich  # adjust import if needed


def run_lead_pipeline(icp: Dict) -> List[Dict]:
    """
    Combines detection and enrichment into a single processing pipeline.
    
    Args:
        icp (Dict): Ideal Customer Profile
    
    Returns:
        List[Dict]: Final enriched leads
    """
    print("==========[🔎] Starting detection phase...===============")
    detected_leads = detection_agent(icp)
    
    print(f"[✅] Detection complete. {len(detected_leads)} leads found.")
    
    print("=======[⚙️] Starting enrichment phase...=======")

    print("detected leads", detected_leads)


    urls = enrich(detected_leads)






    print("==========Enriched=============")
    


