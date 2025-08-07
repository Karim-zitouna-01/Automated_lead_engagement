import os
import json
from dotenv import load_dotenv
from agents import DataConsolidationAgent, EngagementStrategyAgent
import re

def get_company_description(lead_data_path):
    """Lit la description de l'entreprise à partir d'un fichier texte."""
    try:
        with open(os.path.join(lead_data_path, 'company_description.txt'), 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Description de l'entreprise non disponible."

def generate_json_report(markdown_text, company_description):
    json_data = {'company_description': company_description}
    # Extract summary info
    summary_match = re.search(r'\*\*Résumé de Lead :\*\* (.*?) \((.*?)\)', markdown_text)
    if summary_match:
        json_data['nom_prenom'] = summary_match.group(1).strip()
        json_data['titre'] = summary_match.group(2).strip()

    # Split content by sections
    sections = re.split(r'\n\*\*(.*?):\*\*\n', markdown_text)
    
    # First part is before any section, so we ignore it
    sections = sections[1:]

    for i in range(0, len(sections), 2):
        section_title = sections[i].strip()
        section_content = sections[i+1].strip()
        
        # Clean up section title to be a valid JSON key
        section_key = section_title.lower().replace(' ', '_').replace('&', 'et')
        section_key = re.sub(r'\(.*?\)', '', section_key).strip('_')

        # Split content by list items
        items = re.split(r'\n[\*\-]|^\d\.\s', section_content)
        items = [item.strip() for item in items if item.strip()]
        
        if len(items) > 1:
            json_data[section_key] = items
        else:
            json_data[section_key] = section_content

    # Champs obligatoires
    if 'name' not in json_data:
        json_data['name'] = "none"
    if 'company_name' not in json_data:
        json_data['company_name'] = "none"
    if 'linkedin_profile' not in json_data:
        json_data['linkedin_profile'] = "none"

    return json_data

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Erreur: GEMINI_API_KEY non trouvée dans les variables d'environnement.")
        return

    lead_data_path = r"C:\Users\yaola\Videos\formation_2025\Agentic_ai\Automated_lead_engagement\Lead_Engagement\personal_research\profiles\Thierry_Millet"

    print("\n--- Agent 1: Consolidation des données ---")
    consolidation_agent = DataConsolidationAgent(lead_data_path)
    consolidated_report = consolidation_agent.generate_lead_report()
    print("Rapport consolidé généré avec succès.")

    print("\n--- Agent 2: Génération de la stratégie d'engagement ---")
    engagement_strategy_agent = EngagementStrategyAgent(api_key=api_key)
    strategy_output = engagement_strategy_agent.generate_strategy(report_data=consolidated_report)
    print("Stratégie d'engagement générée.")

    # Vérifier si la sortie de l'agent contient une erreur
    if 'error' in strategy_output:
        print(f"Erreur de l'agent: {strategy_output['error']}")
        return

    # Extraire les rapports Markdown et JSON
    markdown_report = strategy_output.get('markdown_report', 'Rapport non généré.')
    json_report_data = strategy_output.get('json_report', {})

    # Sauvegarder le rapport Markdown
    output_file_md = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_lead_report.md")
    with open(output_file_md, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    print(f"Rapport Markdown sauvegardé dans : {output_file_md}")

    # Ajouter la description de l'entreprise et sauvegarder le rapport JSON
    company_description = get_company_description(lead_data_path)
    json_report_data['company_description'] = company_description
    
    output_file_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_lead_report.json")
    with open(output_file_json, 'w', encoding='utf-8') as f:
        json.dump(json_report_data, f, ensure_ascii=False, indent=4)
    print(f"Rapport JSON sauvegardé dans : {output_file_json}")


if __name__ == "__main__":
    main()
