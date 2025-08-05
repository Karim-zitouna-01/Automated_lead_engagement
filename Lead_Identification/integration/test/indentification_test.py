
from integration.identification import run_lead_pipeline
from enrichment.enrichir import enrich

# Mock ICP input
mock_icp = {
    "company_size": "10-50",
    "industry": "Software",
    "location": "Europe"
} 

# Mock outputs
mock_detected_leads = [
    {
  "company_name": "ONEiO",
  "summary": "ONEiO is a next-generation Managed Integration Service Provider that delivers Integration Ops as a Service for IT and technology service providers. They offer a fully managed, continuously optimized service that adapts to business changes automatically, focusing on automating and operating integrations rather than just building them.",
  "reason_for_match": "ONEiO provides AI-enhanced integration services, which aligns with the 'AI Consulting' service in the ICP. They target large enterprises with complex IT environments, which fits the ICP's focus on large company sizes and advanced technology maturity. They also address pain points like operational inefficiencies and data silos.",
  "key_personal": [
    "Petteri Raatikainen (Product Director)"
  ],
  "relevant_urls": [
    "https://www.oneio.cloud/",
    
  ]
},
{
  "company_name": "Salesforce",
  "summary": "This page contains two articles related to AI in the public sector. The first article discusses the AI skills gap in the public sector, based on a Salesforce survey. The second article focuses on how Salesforce's Agentforce and agentic AI can aid overstretched government workers by automating tasks and providing 24/7 availability.",
  "reason_for_match": "The content discusses AI solutions for the public sector, which is a Tier 2 industry in the ICP. It also highlights pain points like operational inefficiencies and the need for automation, aligning with the ICP's pain points and buying motivations.",
  "key_personal": [
    "Casey Coleman, SVP, Global Government Solutions",
    "Josh Gruenbaum, GSA Federal Acquisition Service Commissioner",
    "Dave Rey, President of Salesforce Public Sector",
    "Laura Stanton, FAS Deputy Commissioner",
    "Nasi Jazayeri, Salesforce EVP and GM of Public Sector",
    "Tatum"
  ],
  "relevant_urls": [
    "https://itvmo.gsa.gov/onegov/"
  ]
}

]

mock_enriched_leads = [
    {"name": "Company A", "url": "https://companya.com", "details": "CRM, 50 employees"},
    {"name": "Company B", "url": "https://companyb.com", "details": "Marketing tools, 30 employees"}
]

def enrichement_test():
    enrich(mock_detected_leads)


def identification_test():
    return None

# main function
if __name__ == "__main__":
    print("======starting tests=====")
    print("=====testing enrichement function======== ")
    enrichement_test()
    print("======end of tests ======")
