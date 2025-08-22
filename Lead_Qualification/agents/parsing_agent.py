from typing import Dict, Any
from pathlib import Path
import json
import os
import re
from dotenv import load_dotenv
from google.genai import Client, types  # ✅ Gemini SDK

load_dotenv()

class ParsingAgent:
    def __init__(self):
        # Charger le template de prompt
        self.prompt_template = Path("Lead_Qualification/prompts/parsing_prompt.txt").read_text(encoding="utf-8")
        
        # Clé API Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")
        
        # Initialiser le client Gemini
        self.client = Client(api_key=self.api_key)

    def parse_lead_report(self, report_text: str) -> Dict[str, Any]:
        try:
            # Construction du prompt complet
            full_prompt = f"{self.prompt_template}\n\n{report_text}"

            # Appel à Gemini
            contents = [types.Part.from_text(text=full_prompt)]
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=100000
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents,
                config=config
            )

            raw_output = response.text.strip()

            print("🟡 Réponse brute Gemini :")
            print(raw_output)

            if not raw_output:
                raise Exception("Empty response from Gemini")

            # Extraction robuste du JSON dans la réponse
            json_str = self.extract_json(raw_output)

            # Parsing JSON
            parsed_data = json.loads(json_str)
            return parsed_data

        except json.JSONDecodeError as e:
            print("❌ JSON mal formé :", e)
            print("🔴 Contenu reçu :", raw_output if 'raw_output' in locals() else '')
            raise Exception(f"Parsing error: Invalid JSON format ({e})")
        except Exception as e:
            raise Exception(f"Parsing error: {str(e)}")

    def extract_json(self, text: str) -> str:
        """
        Extrait le premier objet JSON valide dans le texte.
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in Gemini's response.")
        return match.group(0)
