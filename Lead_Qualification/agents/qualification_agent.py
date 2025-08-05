# import json
# import re
# from typing import Tuple
# from pathlib import Path
# import os
# from dotenv import load_dotenv
# from langchain_together import ChatTogether

# load_dotenv()

# class QualificationAgent:
#     def __init__(self):
#         self.prompt_template = Path("prompts/qualification_prompt.txt").read_text(encoding="utf-8")
#         self.api_key = os.getenv("TOGETHER_QUALIFICATION_API_KEY")
#         if not self.api_key:
#             raise ValueError("❌ TOGETHER_QUALIFICATION_API_KEY is missing in your .env file.")
        
#         self.model = ChatTogether(
#             together_api_key=self.api_key,
#             model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
#         )

#     def qualify_lead(self, report_text: str) -> Tuple[float, str]:
#         try:
#             full_prompt = f"{self.prompt_template}\n\n{report_text}"
#             response = self.model.invoke(full_prompt)
#             raw_output = response.content.strip()

#             json_text = self._extract_json(raw_output)
#             cleaned_json = self._clean_json_string(json_text)

#             if not self._validate_json(cleaned_json):
#                 raise Exception("❌ Malformed JSON after cleanup.")

#             parsed = json.loads(cleaned_json)
#             justification = parsed.get("justification", "")
#             score = self._calculate_gpct_score(parsed)

#             return score, justification

#         except json.JSONDecodeError as jde:
#             raise Exception(f"❌ JSON decoding error: {str(jde)}\nRaw JSON: {cleaned_json}")
#         except Exception as e:
#             raise Exception(f"❌ Qualification error: {str(e)}")

#     def _extract_json(self, text: str) -> str:
#         match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
#         if match:
#             return match.group(1).strip()

#         match = re.search(r"\{.*\}", text, re.DOTALL)
#         if match:
#             return match.group(0).strip()

#         return text.strip()

#     def _clean_json_string(self, text: str) -> str:
#         text = text.replace("\u201c", "\"").replace("\u201d", "\"")
#         text = text.replace("\u2018", "'").replace("\u2019", "'")
#         return text.strip()

#     def _validate_json(self, json_str: str) -> bool:
#         try:
#             json.loads(json_str)
#             return True
#         except json.JSONDecodeError:
#             return False

#     def _calculate_gpct_score(self, data: dict) -> float:
#         weights = {
#             "goals": 0.4,
#             "plans": 0.3,
#             "challenges": 0.2,
#             "timeline": 0.1
#         }

#         conversion = {"Low": 1, "Medium": 3, "High": 5}

#         goals = conversion.get(data["goals_assessment"]["strategic_alignment"], 1)
#         plans = conversion.get(data["plans_evidence"]["decision_maker_engagement"], 1)
#         timeline = conversion.get(data["timeline_indicators"]["urgency"], 1)

#         tech_gaps = len(data["challenges_analysis"].get("technology_gaps", []))
#         challenges = max(0, min(5, 5 - tech_gaps))

#         total = (
#             weights["goals"] * goals +
#             weights["plans"] * plans +
#             weights["challenges"] * challenges +
#             weights["timeline"] * timeline
#         ) * 20

#         return round(min(100, max(0, total)), 2)
