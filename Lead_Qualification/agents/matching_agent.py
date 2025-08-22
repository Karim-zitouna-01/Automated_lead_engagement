from typing import Dict, Any, Tuple
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
from google.genai import Client, types  # ✅ Gemini SDK

load_dotenv()

class MatchingAgent:
    def __init__(self):
        # Charger le prompt LLM
        self.prompt_template = Path("Lead_Qualification/prompts/matching_prompt.txt").read_text(encoding="utf-8")
        
        # Charger la clé Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY is missing in your .env file.")
        
        # Initialiser le client Gemini
        self.client = Client(api_key=self.api_key)

        # Charger SBERT Model pour Semantic Similarity
        self.sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def semantic_score(self, icp: Dict[str, Any], lead: Dict[str, Any]) -> float:
        lead_text = lead.get("description", "")
        icp_text = icp.get("target_description", "")

        if not lead_text or not icp_text:
            return 0.0

        embeddings = self.sbert_model.encode([lead_text, icp_text])
        cosine_sim = self.cosine_similarity(embeddings[0], embeddings[1])
        return cosine_sim * 100  # On ramène sur 100 pts

    def cosine_similarity(self, vec1, vec2):
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    def llm_match_score(self, icp: Dict[str, Any], lead: Dict[str, Any], semantic_score: float) -> Tuple[float, str]:
        prompt = f"{self.prompt_template}\n\nICP:\n{json.dumps(icp, indent=2)}\n\nLEAD:\n{json.dumps(lead, indent=2)}\n\nSEMANTIC SCORE (description matching): {semantic_score:.2f}/100\n\nGive the final MATCH SCORE over 100 and justify."
        
        # ✅ Utilisation de Gemini 2.5 Flash Lite
        contents = [types.Part.from_text(text=prompt)]
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=500
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config=config
        )

        raw_output = response.text.strip()  # ✅ Récupération du texte Gemini

        print("🟡 Réponse brute LLM :", raw_output)

        # Parsing JSON response from LLM
        try:
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            json_part = raw_output[json_start:json_end]
            result = json.loads(json_part)

            score = float(result.get("score", 0))
            justification = result.get("justification", "No justification provided.")
            return score, justification

        except Exception:
            raise Exception(f"⚠️ Erreur de parsing JSON. Réponse brute :\n{raw_output}")

    def calculate_match_score(self, icp: Dict[str, Any], lead: Dict[str, Any]) -> Tuple[float, str]:
        try:
            semantic_score = self.semantic_score(icp, lead)
            final_score, justification = self.llm_match_score(icp, lead, semantic_score)
            return final_score, justification

        except Exception as e:
            raise Exception(f"❌ Erreur dans MatchingAgent: {str(e)}")
