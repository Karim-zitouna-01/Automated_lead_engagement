# detection/test/detection_test.py

import json
from detection.detection_agent import analyze_and_detect_duplicates, detection_agent

def test_analyze_and_detect_duplicates():
    leads = [
        {
            "name": "OpenAI",
            "website": "https://openai.com",
            "reason_for_match": "AI research company",
            "key_personal": [
                "Jonni Lundy, COO, Resend",
                "Alexander Mays, Principal Engineer, Forward",
                "Scott Vickers, CTO, Headset",
                "Maximilian Seifert, CTO, Cosuno",
                "Uri Vinetz, Director of Data, Livble",
                "Istvan Kovacs, CTO, Recart",
                "Ben Rogojan, Owner, Seattle Data Guy"
  ],
            
        },
        {
            "name": "OpenAI Inc.",
            "reason_for_match": "Leading in generative AI"
        },
        {
            "name": "OpenAI",
            "reason_for_match": "Developer of ChatGPT"
        },
        {
            "name": "DeepMind",
            "website": "https://deepmind.com",
            "reason_for_match": "AI research lab under Google"
        },
        {
            "name": "Anthropic",
            "website": "https://www.anthropic.com",
            "reason_for_match": "Focused on AI safety"
        },
        {
            "name": "Cohere",
            "website": "https://cohere.ai",
            "reason_for_match": "Provides NLP models"
        },
        {
            "name": "Hugging Face",
            "website": "https://huggingface.co",
            "reason_for_match": "Hosts ML models and datasets",
            
        },
    ]

    cleaned_list_leads=analyze_and_detect_duplicates(leads)
    for lead in cleaned_list_leads:
        print(lead)


def test_detection_agent():
    # This function would typically call the detection_agent function
    # and check if it returns the expected results.
    icp={
  "service": "AI Consulting",
  "ideal_customer_profile": {
    "industry": {
      "tier1_core_focus": [
        "Banking & Financial Services",
        "Insurance",
        "Energy & Utilities",
        "Manufacturing & Automotive"
      ],
      "tier2_opportunistic_growth": [
        "Telecommunications & Media",
        "Public Sector & Government",
        "Transport & Logistics",
        "Retail"
      ]
    },
    "company_size": {
      "employees": {
        "min": 2000
      },
      "annual_revenue_eur": {
        "min": 500000000
      }
    },
    "geography": [
      "Francophone Europe (France, Belgium, Switzerland, Luxembourg)",
      "Domestic Tunisian Market",
      "Broader EMEA (English-speaking Europe, Middle East)"
    ],
    "technology_maturity": "Advanced",
    "existing_stack": [
      "SAP (S/4HANA)",
      "Microsoft Dynamics 365",
      "Oracle",
      "Microsoft Azure",
      "AWS",
      "Google Cloud Platform",
      "Informatica",
      "NoSQL databases",
      "Data lake/data mesh architectures"
    ],
    "key_decision_makers": [
      "Chief Financial Officer (CFO)",
      "Chief Operating Officer (COO)",
      "Chief Information Officer (CIO)",
      "Chief Technology Officer (CTO)",
      "Chief Data Officer (CDO)",
      "Head of Innovation",
      "VP of Supply Chain",
      "Head of Customer Service",
      "Plant Manager"
    ],
    "pain_points": [
      "Operational inefficiencies from manual processes",
      "Complex regulatory and compliance burdens",
      "Data silos and underutilized 'dark data'",
      "Competitive disruption from data-native competitors",
      "Scarcity and high cost of AI/data science talent"
    ],
    "buying_motivation": [
      "Scale AI from pilot projects to enterprise-wide solutions",
      "Leverage data for strategic decision-making",
      "Achieve compliance through automated monitoring",
      "Unlock value from existing data assets",
      "Access cost-effective, high-quality AI talent"
    ],
    "budget": {
      "consulting_project_range_eur": {
        "min": 500000,
        "max": 5000000
      }
    },
    "business_goals": [
      "Foster a data-driven culture",
      "Achieve positive innovation aligned with ESG principles",
      "Build organizational resilience",
      "Transform customer experience with personalization",
      "Optimize supply chain and operational efficiency"
    ],
    "sales_cycle_duration": "4 to 8 months",
    "preferred_engagement_model": [
      "AI Foundation Package (data maturity assessment, governance, roadmap)",
      "Nearshore Co-Development Team (dedicated AI/data science pod)",
      "Solution-in-a-Box (pre-packaged industry-specific AI accelerators)"
    ],
    "buying_triggers": [
      "Recent C-suite appointment (CDO, CIO, CDO, Innovation Head)",
      "Public announcement of digital transformation or AI initiative",
      "Merger and acquisition activity requiring system integration",
      "Spike in hiring for data scientists and AI specialists"
    ],
    "preferred_channels": [
      "Industry publications (Financial Times, Les Echos, L'Usine Nouvelle)",
      "Analyst reports (Gartner, Forrester, IDC)",
      "Professional networks (LinkedIn)",
      "Industry events (World AI Cannes Festival, Swiss Data & AI Summit)"
    ]
  }
}
    
    print("Running detection agent test...")
    leads = detection_agent(icp)
    #store leads in txt file
    with open("detection_agent_test_output.txt", "w") as f:
        for lead in leads:
            f.write(json.dumps(lead, indent=2) + "\n")
    


if __name__ == "__main__":
    print("Starting tests...")
    test_detection_agent()
    print("All tests completed successfully.")
    
