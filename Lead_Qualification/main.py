from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import json
from datetime import datetime
import uuid
import sys

from fpdf import FPDF

from agents.parsing_agent import ParsingAgent
from agents.matching_agent import MatchingAgent
from agents.qualification_agent import QualificationAgent
from agents.scoring_agent import ScoringAgent
from utils.file_manager import FileManager

app = FastAPI()
file_manager = FileManager()
sys.stdout.reconfigure(encoding='utf-8')

# Initialisation des agents
parsing_agent = ParsingAgent()
matching_agent = MatchingAgent()
qualification_agent = QualificationAgent()
scoring_agent = ScoringAgent()


def sanitize_for_pdf(text: str) -> str:
    """Nettoie une chaîne pour FPDF (latin-1 compatible)."""
    if not text:
        return ""
    return text.encode('latin-1', errors='replace').decode('latin-1')


@app.on_event("startup")
async def process_all_leads():
    try:
        print("🚀 Traitement automatique des leads en cours...")
        rapport_dir = Path(__file__).parent / "data" / "rapports"
        icp_path = Path(__file__).parent / "data" / "icp.json"
        output_pdf_path = Path(__file__).parent / "data" / "rapport_final.pdf"

        with open(icp_path, 'r', encoding='utf-8') as f:
            icp = json.load(f)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Rapport de Qualification des Leads", ln=True, align='C')
        pdf.ln(10)

        for report_file in rapport_dir.glob("*.txt"):
            company_name = report_file.stem
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_text = f.read()

                print(f"📝 Traitement du lead : {company_name}")
                parsed_lead = parsing_agent.parse_lead_report(report_text)

                # Matching
                match_score, match_justification = matching_agent.calculate_match_score(icp, parsed_lead)

                # Qualification
                qualification_score, qualification_justification = qualification_agent.qualify_lead(report_text)
                  # Ajoute cette ligne pour afficher la justification dans la console
                print(f"🎯 Qualification Justification for {company_name}:\n{qualification_justification}\n")

                # Scoring final
                final_score, classification, final_justification = scoring_agent.score_lead(
                    match_score,
                    match_justification,
                    qualification_score,
                    qualification_justification
                )

                # Génération PDF
                pdf.set_font("Arial", style='B', size=12)
                pdf.cell(0, 10, sanitize_for_pdf(company_name), ln=True)
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 10, f"- ICP Match: {match_score:.1f}/100", ln=True)
                pdf.cell(0, 10, f"- GPCT Score: {qualification_score:.1f}/100", ln=True)
                pdf.cell(0, 10, f"- Final Score: {final_score:.1f}/100", ln=True)
                pdf.cell(0, 10, f"- Classification: {sanitize_for_pdf(classification.upper())}", ln=True)
                pdf.multi_cell(0, 10, f"Justification: {sanitize_for_pdf(final_justification)}")
                pdf.ln(5)

            except Exception as e:
                print(f"❌ Erreur pour le lead {company_name} : {str(e)}")
                pdf.set_font("Arial", style='B', size=12)
                pdf.cell(0, 10, sanitize_for_pdf(company_name), ln=True)
                pdf.set_font("Arial", size=11)
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, sanitize_for_pdf(f"Erreur : {str(e)}"), ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)

        pdf.output(output_pdf_path)
        print(f"✅ Rapport PDF généré : {output_pdf_path}")

    except Exception as e:
        print("❗ Erreur critique lors du traitement des leads :", str(e))


@app.post("/api/process_lead")
async def process_lead_report(file: UploadFile = File(...)):
    try:
        content = await file.read()
        report_text = content.decode("utf-8")
        filename = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}.txt"
        file_manager.save_lead_report(filename, report_text)

        parsed_lead = parsing_agent.parse_lead_report(report_text)
        icp = file_manager.load_icp()

        # Matching
        match_score, match_justification = matching_agent.calculate_match_score(icp, parsed_lead)

        # Qualification
        qualification_score, qualification_justification = qualification_agent.qualify_lead(report_text)

        # Scoring final
        final_score, classification, final_justification = scoring_agent.score_lead(
            match_score,
            match_justification,
            qualification_score,
            qualification_justification
        )

        return {
            "status": "success",
            "lead_id": parsed_lead.get("lead_id"),
            "company": parsed_lead.get("company_name"),
            "scores": {
                "icp_match": round(match_score, 1),
                "gpct_score": round(qualification_score, 1),
                "final_score": round(final_score, 1)
            },
            "classification": classification,
            "justification": final_justification,
            "details": {
                "parsed_data": parsed_lead,
                "qualification": {
                    "gpct_score": qualification_score,
                    "justification": qualification_justification
                }
            }
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Erreur JSON : réponse malformée ou vide.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/icp")
async def get_current_icp():
    try:
        return file_manager.load_icp()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
