# scripts/insert_service.py

from server.common.firebase_config import db  # assumes this is your firestore client
import uuid
from datetime import datetime

def insert_sample_service():
    service_id = str(uuid.uuid4())

    service_data = {
        "id": service_id,
        "name": "AI Consulting",
        "icp": {
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
},
        "generation_status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    db.collection("services").document(service_id).set(service_data)
    print(f"✅ Inserted service with id: {service_id}")

if __name__ == "__main__":
    insert_sample_service()


