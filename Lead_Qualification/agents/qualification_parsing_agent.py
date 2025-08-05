import json
import re
from typing import Dict
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_together import ChatTogether

load_dotenv()

class QualificationParsingAgent:
    def __init__(self):
        self.prompt_template = Path("prompts/qualification_parsing_prompt.txt").read_text(encoding="utf-8")
        self.api_key = os.getenv("TOGETHER_qualification_parsing_API_KEY")
        if not self.api_key:
            raise ValueError("\u274c TOGETHER_QUALIFICATION_API_KEY is missing in your .env file.")

        self.model = ChatTogether(
            together_api_key=self.api_key,
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        )

    def parse_report(self, report_text: str) -> Dict:
        parsing_prompt = f"{self.prompt_template}\n\n{report_text}"
        response = self.model.invoke(parsing_prompt)
        parsed_json = self._extract_and_validate_json(response.content.strip())
        return parsed_json

    def _extract_and_validate_json(self, text: str) -> Dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise Exception(f"\u274c Parsing Phase: No JSON found.\nResponse: {text}")

        json_str = self._clean_json_string(match.group(0))

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as jde:
            raise Exception(f"\u274c Parsing Phase: JSON Decode Error: {str(jde)}\nRaw JSON: {json_str}")

    def _clean_json_string(self, text: str) -> str:
        text = text.replace("\u201c", "\"").replace("\u201d", "\"")
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        return text.strip()