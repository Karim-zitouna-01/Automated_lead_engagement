from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import json
from datetime import datetime
import uuid
import sys

from fpdf import FPDF

from agents.parsing_agent import ParsingAgent
from agents.matching_agent import MatchingAgent
from agents.qualification_parsing_agent import QualificationParsingAgent
from agents.qualification_judge_agent import QualificationJudgeAgent
from agents.scoring_agent import ScoringAgent
from utils.file_manager import FileManager

app = FastAPI()
file_manager = FileManager()
sys.stdout.reconfigure(encoding='utf-8')

# Initialisation des agents
parsing_agent = ParsingAgent()
matching_agent = MatchingAgent()
qualification_parsing_agent = QualificationParsingAgent()
qualification_judge_agent = QualificationJudgeAgent()
scoring_agent = ScoringAgent()


def sanitize_for_pdf(text: str) -> str:
    """Nettoie une chaîne pour FPDF (latin-1 compatible)."""
    if not text:
        return ""
    return text.encode('latin-1', errors='replace').decode('latin-1')


def score_color(score: float) -> tuple:
    """Retourne une couleur RGB selon la valeur du score (0-100)."""
    if score >= 75:
        return (0, 128, 0)   # Vert foncé
    elif score >= 40:
        return (255, 140, 0) # Orange foncé
    else:
        return (178, 34, 34) # Rouge foncé


def add_score_bar(pdf, score: float, x: int, y: int, width: int = 100, height: int = 10):
    """Ajoute une barre de score visuelle."""
    pdf.set_fill_color(220, 220, 220)
    pdf.rect(x, y, width, height, 'F')

    progress_width = (score / 100) * width
    r, g, b = score_color(score)
    pdf.set_fill_color(r, g, b)
    pdf.rect(x, y, progress_width, height, 'F')

    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(x, y + (height / 2) - 3)
    pdf.cell(width, 5, f"{score:.1f}%", 0, 0, 'C')


def add_header(pdf):
    """Ajoute un en-tête professionnel au rapport."""
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "RAPPORT DE QUALIFICATION DES LEADS", 0, 1, 'C')

    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, datetime.now().strftime("Généré le %d/%m/%Y à %H:%M"), 0, 1, 'C')
    pdf.ln(10)


def add_footer(pdf):
    """Ajoute un pied de page."""
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')


def create_lead_section(pdf, lead_data):
    """Crée une section visuelle pour chaque lead."""
    pdf.set_fill_color(240, 248, 255)
    pdf.rect(10, pdf.get_y(), 190, 10, 'F')

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, sanitize_for_pdf(lead_data['company_name']), 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 8, "CRITÈRE", 1, 0, 'C')
    pdf.cell(40, 8, "SCORE", 1, 1, 'C')

    pdf.set_font("Arial", '', 10)
    pdf.cell(90, 8, "Match ICP", 1)
    r, g, b = score_color(lead_data['match_score'])
    pdf.set_text_color(r, g, b)
    pdf.cell(40, 8, f"{lead_data['match_score']:.1f}%", 1, 1, 'C')
    pdf.set_text_color(0, 0, 0)

    pdf.cell(90, 8, "Score GPCT", 1)
    r, g, b = score_color(lead_data['qualification_score'])
    pdf.set_text_color(r, g, b)
    pdf.cell(40, 8, f"{lead_data['qualification_score']:.1f}%", 1, 1, 'C')
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 8, "SCORE FINAL", 1)
    r, g, b = score_color(lead_data['final_score'])
    pdf.set_text_color(r, g, b)
    pdf.cell(40, 8, f"{lead_data['final_score']:.1f}%", 1, 1, 'C')
    pdf.set_text_color(0, 0, 0)

    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(130, 8, lead_data['classification'].upper(), 1, 1, 'C', True)

    pdf.ln(5)
    pdf.cell(40, 8, "Niveau de qualification:")
    add_score_bar(pdf, lead_data['final_score'], pdf.get_x(), pdf.get_y())
    pdf.ln(15)

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Analyse:", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, sanitize_for_pdf(lead_data['justification']))
    pdf.ln(10)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)


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
        add_header(pdf)

        leads_data = []

        for report_file in rapport_dir.glob("*.txt"):
            company_name = report_file.stem
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_text = f.read()

                print(f"📝 Traitement du lead : {company_name}")
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
                    "company_name": company_name,
                    "match_score": match_score,
                    "match_justification": match_justification,
                    "qualification_score": qualification_score,
                    "qualification_justification": qualification_justification,
                    **scoring_result
                })
            except Exception as e:
                print(f"❌ Erreur pour le lead {company_name} : {str(e)}")
                leads_data.append({
                    "company_name": company_name,
                    "error": str(e)
                })

        # Tableau récap
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Synthèse des Leads", 0, 1)
        pdf.ln(5)

        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(80, 8, "Entreprise", 1, 0, 'C', True)
        pdf.cell(30, 8, "Match ICP", 1, 0, 'C', True)
        pdf.cell(30, 8, "Score GPCT", 1, 0, 'C', True)
        pdf.cell(30, 8, "Score Final", 1, 0, 'C', True)
        pdf.cell(20, 8, "Class.", 1, 1, 'C', True)

        pdf.set_font("Arial", '', 9)
        for lead in leads_data:
            if 'error' in lead:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(80, 8, sanitize_for_pdf(lead['company_name'][:30]), 1)
                pdf.cell(110, 8, f"Erreur: {lead['error'][:30]}", 1, 1)
                continue

            pdf.set_text_color(0, 0, 0)
            pdf.cell(80, 8, sanitize_for_pdf(lead['company_name'][:30]), 1)

            r, g, b = score_color(lead['match_score'])
            pdf.set_text_color(r, g, b)
            pdf.cell(30, 8, f"{lead['match_score']:.1f}%", 1, 0, 'C')

            r, g, b = score_color(lead['qualification_score'])
            pdf.set_text_color(r, g, b)
            pdf.cell(30, 8, f"{lead['qualification_score']:.1f}%", 1, 0, 'C')

            r, g, b = score_color(lead['final_score'])
            pdf.set_text_color(r, g, b)
            pdf.cell(30, 8, f"{lead['final_score']:.1f}%", 1, 0, 'C')

            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(20, 8, lead['classification'][:4], 1, 1, 'C', True)

        pdf.ln(15)

        # Sections détaillées
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Analyses Détaillées", 0, 1)
        pdf.ln(10)

        for lead in leads_data:
            if 'error' in lead:
                continue
            if pdf.get_y() > 250:
                pdf.add_page()
                add_header(pdf)
                pdf.ln(10)
            create_lead_section(pdf, lead)

        add_footer(pdf)
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

        match_score, match_justification = matching_agent.calculate_match_score(icp, parsed_lead)
        parsed_gcpt = qualification_parsing_agent.parse_report(report_text)
        qualification_score, qualification_justification = qualification_judge_agent.judge_gcpt(parsed_gcpt)

        scoring_result = scoring_agent.score_lead(
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
                "final_score": round(scoring_result['final_score'], 1)
            },
            "classification": scoring_result['classification'],
            "justification": scoring_result['justification'],
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
