import os
import requests
from typing import Tuple

class ScoringAgent:
    def __init__(self):
        self.api_key = os.getenv("TOGETHER_SCORING_API_KEY")
        if not self.api_key:
            raise ValueError("❌ TOGETHER_SCORING_API_KEY is not set in environment variables.")

        self.llm_url = "https://api.together.xyz/inference"
        self.model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    def score_lead(
        self,
        match_score: float,
        match_justification: str,
        qualification_score: float,
        qualification_justification: str
    ) -> Tuple[float, str, str]:
        """
        Calcule le score final, la classification (Hot/Cold), et la justification finale.
        Retourne : (final_score, classification, final_justification)
        """
        try:
            # Score pondéré
            final_score = round(match_score * 0.7 + qualification_score * 0.3, 1)

            # Classification
            classification = "Hot" if final_score >= 75 else "Cold"

            # Justification finale
            final_justification = self._generate_final_justification(
                match_justification,
                qualification_justification,
                final_score,
                classification
            )

            return final_score, classification, final_justification

        except Exception as e:
            raise Exception(f"❌ ScoringAgent error: {str(e)}")

    def _generate_final_justification(
        self,
        match_justification: str,
        qualification_justification: str,
        final_score: float,
        classification: str
    ) -> str:
        """
        Génère une justification courte et professionnelle pour la classification du lead.
        """
        prompt = f"""
You are a senior sales analyst tasked with summarizing lead evaluation results.

You are given two inputs:
1. Matching justification — analysis of how well the lead fits our Ideal Customer Profile (ICP).
2. Qualification justification — analysis based on the GPCT framework (Goals, Plans, Challenges, Timeline).

Here are the inputs:
--- 
MATCHING JUSTIFICATION:
{match_justification}

QUALIFICATION JUSTIFICATION:
{qualification_justification}

FINAL SCORE: {final_score}/100
CLASSIFICATION: {classification}
---

Your task:
- Write a single, clear, and concise paragraph (max 4 lines) that explains why the lead was classified as {classification}, based on the combined insights from matching and qualification.
- Do not repeat full sentences from the inputs. Instead, synthesize key points (e.g., alignment, gaps, urgency, decision-makers, maturity).
- Use professional tone. No bullet points. No repetition.
- Goal: Help a sales executive quickly understand the decision.

Respond with only the paragraph. Do not include labels, headers, or explanations.
"""

        response = requests.post(
            self.llm_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": 150,
                "temperature": 0.3,
                "top_p": 0.9
            }
        )

        if response.status_code == 200:
            json_response = response.json()
            try:
                # Extraction robuste du texte généré
                text = None
                if "output" in json_response:
                    output = json_response["output"]
                    if isinstance(output, str):
                        text = output
                    elif isinstance(output, dict) and "choices" in output:
                        text = output["choices"][0].get("text", None)
                if not text and "choices" in json_response:
                    text = json_response["choices"][0].get("text", None)

                if text and isinstance(text, str):
                    return text.strip() if text.strip() else "Justification not available."
                else:
                    raise Exception("❌ Invalid LLM response format: text not found.")
            except (KeyError, IndexError, TypeError) as e:
                raise Exception(f"❌ Invalid LLM response format: {str(e)}")
        else:
            raise Exception(
                f"❌ LLM justification generation failed: {response.status_code} - {response.text}"
            )
