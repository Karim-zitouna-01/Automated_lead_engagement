from typing import Dict, Any, Tuple
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from langchain_together import ChatTogether

load_dotenv()

class MatchingAgent:
    def __init__(self):
        self.prompt_template = Path("prompts/matching_prompt.txt").read_text(encoding="utf-8")

        self.api_key = os.getenv("TOGETHER_MATCHING_API_KEY")
        if not self.api_key:
            raise ValueError("❌ TOGETHER_MATCHING_API_KEY is missing in your .env file.")

        self.model = ChatTogether(
            together_api_key=self.api_key,
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        )

    def calculate_match_score(self, icp: Dict[str, Any], lead: Dict[str, Any]) -> Tuple[float, str]:
        try:
            prompt = f"{self.prompt_template}\n\nICP:\n{json.dumps(icp, indent=2)}\n\nLEAD:\n{json.dumps(lead, indent=2)}"
            response = self.model.invoke(prompt)
            raw_output = response.content.strip()

            print("🟡 Réponse brute :", raw_output)

            try:
                # Forcer la détection même si le modèle ajoute du texte autour
                json_start = raw_output.find('{')
                json_end = raw_output.rfind('}') + 1
                json_part = raw_output[json_start:json_end]
                result = json.loads(json_part)

                score = float(result.get("score", 0))
                justification = result.get("justification", "No justification provided.")
                return score, justification

            except Exception as parse_err:
                raise Exception(f"⚠️ Erreur de parsing JSON. Réponse brute :\n{raw_output}")

        except Exception as e:
            raise Exception(f"❌ Erreur dans MatchingAgent: {str(e)}")
