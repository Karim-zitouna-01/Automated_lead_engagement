import json
import re
from typing import Dict
from pathlib import Path
import os
from dotenv import load_dotenv
from google.genai import Client, types  # ✅ Gemini SDK

load_dotenv()

class QualificationParsingAgent:
    def __init__(self):
        # Charger le prompt
        self.prompt_template = Path(
            "Lead_Qualification/prompts/qualification_parsing_prompt.txt"
        ).read_text(encoding="utf-8")

        # Clé API Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY is missing in your .env file.")

        # Client Gemini
        self.client = Client(api_key=self.api_key)

    def parse_report(self, report_text: str) -> Dict:
        parsing_prompt = f"{self.prompt_template}\n\n{report_text}"

        # Construire la requête Gemini
        contents = [types.Part.from_text(text=parsing_prompt)]
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
        return self._extract_and_validate_json(raw_output)

    def _extract_and_validate_json(self, text: str) -> Dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise Exception(f"❌ Parsing Phase: No JSON found.\nResponse: {text}")

        json_str = self._clean_json_string(match.group(0))

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as jde:
            raise Exception(f"❌ Parsing Phase: JSON Decode Error: {str(jde)}\nRaw JSON: {json_str}")

    def _clean_json_string(self, text: str) -> str:
        text = text.replace("\u201c", "\"").replace("\u201d", "\"")
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        return text.strip()
