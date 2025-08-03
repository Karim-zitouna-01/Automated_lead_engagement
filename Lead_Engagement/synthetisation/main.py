import os
import json
from pathlib import Path
from dotenv import load_dotenv
from data_cleaners.linkedin_cleaner import LinkedInCleaner
from data_cleaners.instagram_cleaner import InstagramCleaner
from data_cleaners.twitter_cleaner import TwitterCleaner
from agents import DataConsolidationAgent, EngagementStrategyAgent

# Dictionnaire des cleaners par plateforme
PLATFORM_CLEANERS = {
    "twitter": TwitterCleaner,
    "linkedin": LinkedInCleaner,
    "instagram": InstagramCleaner
}

def clean_and_save(input_file: Path, platform: str):
    try:
        raw_content = input_file.read_text(encoding='utf-8')
        cleaner = PLATFORM_CLEANERS.get(platform.lower())
        if cleaner is None:
            print(f"⚠️ Plateforme non supportée: {platform} ({input_file})")
            return

        cleaned_data = cleaner.clean(raw_content)
        output_file = input_file.with_name(f"{input_file.stem}_cleaned.json")
        output_file.write_text(json.dumps(cleaned_data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"✅ {platform.title()} nettoyé: {output_file}")
    except Exception as e:
        print(f"❌ Erreur de nettoyage pour {input_file}: {e}")

def process_person(person_dir: Path, entreprise: str):
    print(f"\n🔍 Traitement de {person_dir.name} ({entreprise})")
    
    # 1. Nettoyage des données sociales
    for platform in PLATFORM_CLEANERS:
        input_file = person_dir / f"{platform}.txt"
        if input_file.exists():
            clean_and_save(input_file, platform)
    
    # 2. Lancer les agents sur les données nettoyées
    try:
        # Agent 1 : Consolidation
        consolidation_agent = DataConsolidationAgent(str(person_dir))
        consolidated_report = consolidation_agent.generate_lead_report()
        print(f"📄 Rapport consolidé généré pour {person_dir.name}.")

        # Agent 2 : Stratégie d'engagement
        engagement_agent = EngagementStrategyAgent(api_key=os.getenv("GEMINI_API_KEY"))
        final_strategy = engagement_agent.generate_strategy(report_data=consolidated_report)
        print(f"🎯 Stratégie d'engagement générée pour {person_dir.name}.")

        # 3. Sauvegarde du rapport markdown
        output_dir = Path("outputs") / entreprise / person_dir.name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "lead_report.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_strategy)

        print(f"✅ Rapport sauvegardé : {output_path}")
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement des agents pour {person_dir.name}: {e}")

def main(data_root: str = "data"):
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Clé API GEMINI_API_KEY manquante.")
        return

    root_path = Path(data_root)
    for company_dir in root_path.iterdir():
        if company_dir.is_dir():
            for person_dir in company_dir.iterdir():
                if person_dir.is_dir():
                    process_person(person_dir, entreprise=company_dir.name)

if __name__ == "__main__":
    main()
