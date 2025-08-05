from typing import Dict, Any
from pathlib import Path
import json
import os
import re
from dotenv import load_dotenv
from langchain_together import ChatTogether

load_dotenv()

class ParsingAgent:
    def __init__(self):
        # Charger le template de prompt
        self.prompt_template = Path("prompts/parsing_prompt.txt").read_text(encoding="utf-8")
        
        # Clé API dédiée pour ce agent (Together)
        self.api_key = os.getenv("TOGETHER_PARSING_API_KEY")
        if not self.api_key:
            raise ValueError("❌ TOGETHER_PARSING_API_KEY not found in environment variables.")
        
        # Initialiser le client Together avec le modèle choisi
        self.chat = ChatTogether(
            together_api_key=self.api_key,
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        )

    def parse_lead_report(self, report_text: str) -> Dict[str, Any]:
        try:
            # Construction du prompt complet
            full_prompt = f"{self.prompt_template}\n\n{report_text}"

            # Appel au modèle (non streaming, réponse complète)
            response = self.chat.invoke(full_prompt)

            print("🟡 Réponse brute de Together :")
            print(response.content)

            if not response.content.strip():
                raise Exception("Empty response from Together")

            # Extraction robuste du JSON dans la réponse
            json_str = self.extract_json(response.content)

            # Parsing JSON
            parsed_data = json.loads(json_str)
            return parsed_data

        except json.JSONDecodeError as e:
            print("❌ JSON mal formé :", e)
            print("🔴 Contenu reçu :", response.content if 'response' in locals() else '')
            raise Exception(f"Parsing error: Invalid JSON format ({e})")
        except Exception as e:
            raise Exception(f"Parsing error: {str(e)}")

    def extract_json(self, text: str) -> str:
        """
        Extrait le premier objet JSON valide dans le texte.
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in Together's response.")
        return match.group(0)
