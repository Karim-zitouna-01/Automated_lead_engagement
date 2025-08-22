import json
import re
from typing import Dict, Tuple
from pathlib import Path
import os
from dotenv import load_dotenv
from google.genai import Client, types  # ✅ Gemini SDK

load_dotenv()

class QualificationJudgeAgent:
    def __init__(self):
        # Charger le prompt
        self.prompt_template = Path(
            "Lead_Qualification/prompts/qualification_judge_prompt.txt"
        ).read_text(encoding="utf-8")

        # Clé API Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY is missing in your .env file.")

        # Client Gemini
        self.client = Client(api_key=self.api_key)

    def judge_gcpt(self, parsed_gcpt: Dict) -> Tuple[float, str]:
        judge_prompt = f"{self.prompt_template}\n\n{json.dumps(parsed_gcpt, indent=2)}"

        # Préparer la requête Gemini
        contents = [types.Part.from_text(text=judge_prompt)]
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=100000
        )

        # Appel API Gemini
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config=config
        )

        raw_output = response.text.strip()

        judged_gcpt = self._extract_and_validate_json(raw_output)

        score = self._calculate_gpct_score(judged_gcpt)
        justification = judged_gcpt.get("justification", "No justification provided.")

        return score, justification

    def _extract_and_validate_json(self, text: str) -> Dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise Exception(f"❌ Judge Phase: No JSON found.\nResponse: {text}")

        json_str = self._clean_json_string(match.group(0))

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as jde:
            raise Exception(f"❌ Judge Phase: JSON Decode Error: {str(jde)}\nRaw JSON: {json_str}")

    def _clean_json_string(self, text: str) -> str:
        text = text.replace("\u201c", "\"").replace("\u201d", "\"")
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        return text.strip()

    def _calculate_gpct_score(self, data: dict) -> float:
        weights = {
            "goals": 0.4,
            "plans": 0.3,
            "challenges": 0.2,
            "timeline": 0.1
        }

        conversion = {"Low": 1, "Medium": 3, "High": 5}

        goals = conversion.get(data["goals_assessment"]["strategic_alignment"], 1)
        plans = conversion.get(data["plans_evidence"]["decision_maker_engagement"], 1)
        timeline = conversion.get(data["timeline_indicators"]["urgency"], 1)

        tech_gaps = len(data["challenges_analysis"].get("technology_gaps", []))
        challenges = max(0, min(5, 5 - tech_gaps))

        total = (
            weights["goals"] * goals +
            weights["plans"] * plans +
            weights["challenges"] * challenges +
            weights["timeline"] * timeline
        ) * 20

        return round(min(100, max(0, total)), 2)
