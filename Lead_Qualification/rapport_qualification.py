# rapport_qualification.py
from fpdf import FPDF
from datetime import datetime
from pathlib import Path

def sanitize_for_pdf(text: str) -> str:
    if not text:
        return ""
    return text.encode('latin-1', errors='replace').decode('latin-1')

def score_color(score: float) -> tuple:
    if score >= 75:
        return (0, 128, 0)
    elif score >= 40:
        return (255, 140, 0)
    else:
        return (178, 34, 34)

def add_score_bar(pdf, score: float, x: int, y: int, width: int = 100, height: int = 10):
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
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "RAPPORT DE QUALIFICATION DES LEADS", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, datetime.now().strftime("Généré le %d/%m/%Y à %H:%M"), 0, 1, 'C')
    pdf.ln(10)

def add_footer(pdf):
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')

def create_lead_section(pdf, lead_data):
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

def generer_rapport_pdf(leads_data, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    add_header(pdf)

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
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Analyses Détaillées", 0, 1)
    pdf.ln(10)
    for lead in leads_data:
        create_lead_section(pdf, lead)

    add_footer(pdf)
    pdf.output(output_path)
    return output_path
