import os
import requests
from firebase_admin import credentials, firestore, initialize_app
from rapport_qualification import generer_rapport_pdf
from agents.parsing_agent import ParsingAgent
from agents.matching_agent import MatchingAgent
from agents.qualification_parsing_agent import QualificationParsingAgent
from agents.qualification_judge_agent import QualificationJudgeAgent
from agents.scoring_agent import ScoringAgent

# ==== CONFIG ====
service_id_input = "71241f00-6c10-434c-a79d-4da427b9f856"  # <-- à remplacer par le service_id voulu

# Initialisation des agents
parsing_agent = ParsingAgent()
matching_agent = MatchingAgent()
qualification_parsing_agent = QualificationParsingAgent()
qualification_judge_agent = QualificationJudgeAgent()
scoring_agent = ScoringAgent()

# Connexion à Firebase
cred = credentials.Certificate("firebase_key.json")  # Ton fichier clé Firebase
initialize_app(cred)
db = firestore.client()

def process_leads():
    leads_data = []

    # Créer le dossier outputs si inexistant
    os.makedirs("outputs", exist_ok=True)

    # ==== Récupération de l'ICP pour ce service ====
    service_doc = db.collection("services").document(service_id_input).get()
    if not service_doc.exists:
        print(f"❌ Service ID {service_id_input} introuvable dans 'services'")
        return
    icp = service_doc.to_dict().get("icp", {})
    print(f"✅ ICP récupéré pour service {service_id_input}")

    # ==== Récupération des leads pour ce service ====
    leads = db.collection("Leads").where("service_id", "==", service_id_input).stream()

    for lead in leads:
        lead_data = lead.to_dict()
        report_url = lead_data.get("report_url")

        print(f"📄 Traitement du lead : {lead.id}")

        if not report_url:
            print(f"⚠ Lead {lead.id} n'a pas de report_url")
            continue

        # Télécharger le rapport depuis Cloudinary
        try:
            response = requests.get(report_url)
            if response.status_code != 200:
                print(f"⚠ Impossible de télécharger {report_url}")
                continue
            report_text = response.text
        except Exception as e:
            print(f"⚠ Erreur téléchargement {report_url} : {e}")
            continue

        # Analyse du lead
        try:
            parsed_lead = parsing_agent.parse_lead_report(report_text)
            match_score, match_justification = matching_agent.calculate_match_score(icp, parsed_lead)
            parsed_gcpt = qualification_parsing_agent.parse_report(report_text)
            qualification_score, qualification_justification = qualification_judge_agent.judge_gcpt(parsed_gcpt)
            scoring_result = scoring_agent.score_lead(
                match_score,
                match_justification,
                qualification_score,
                qualification_justification
            )

            leads_data.append({
                "company_name": parsed_lead.get("company_name", "Inconnu"),
                "match_score": match_score,
                "qualification_score": qualification_score,
                "final_score": scoring_result["final_score"],
                "classification": scoring_result["classification"],
                "justification": scoring_result["justification"]
            })
        except Exception as e:
            print(f"⚠ Erreur analyse lead {lead.id} : {e}")
            continue

    # ==== Génération du rapport PDF ====
    if leads_data:
        output_path = os.path.join("outputs", "rapport_final.pdf")
        generer_rapport_pdf(leads_data, output_path)
        print(f"✅ Rapport PDF généré : {output_path}")
    else:
        print("⚠ Aucun lead analysé, pas de PDF généré.")

if __name__ == "__main__":
    process_leads()
