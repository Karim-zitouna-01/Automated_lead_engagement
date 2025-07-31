import os
import json
from dotenv import load_dotenv
from agents import DataConsolidationAgent, EngagementStrategyAgent

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Erreur: GEMINI_API_KEY non trouvée dans les variables d'environnement.")
        return

    # Chemin vers les données du lead (exemple pour Imen Ayari)
    lead_data_path = r"C:\Users\yaola\Videos\formation_2025\Agentic_ai\Roua_task\data\Talan\ImenAyari"

    # --- Agent 1: Consolidation des données ---
    print("\n--- Agent 1: Consolidation des données ---")
    consolidation_agent = DataConsolidationAgent(lead_data_path)
    consolidated_report = consolidation_agent.generate_lead_report()
    print("Rapport consolidé généré avec succès.")

    # --- Agent 2: Génération de la stratégie d'engagement ---
    print("\n--- Agent 2: Génération de la stratégie d'engagement ---")
    engagement_strategy_agent = EngagementStrategyAgent(api_key=api_key)
    final_strategy = engagement_strategy_agent.generate_strategy(report_data=consolidated_report)
    print("Stratégie d'engagement générée.")

    # Sauvegarder le rapport Markdown à la racine du projet
    output_file_md = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imen_ayari_lead_report.md")
    
    with open(output_file_md, 'w', encoding='utf-8') as f:
        f.write(final_strategy)
    
    print(f"Rapport Markdown pour Imen Ayari généré et sauvegardé dans : {output_file_md}")

if __name__ == "__main__":
    main()
