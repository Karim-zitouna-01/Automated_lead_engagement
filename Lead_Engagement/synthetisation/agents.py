import json
import os
import google.generativeai as genai

class DataConsolidationAgent:
    def __init__(self, lead_data_path: str):
        self.lead_data_path = lead_data_path

    def _load_json_data(self, file_name: str):
        """Charge un fichier JSON en toute sécurité."""
        file_path = os.path.join(self.lead_data_path, file_name)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Avertissement: Impossible de lire ou parser {file_path}: {e}")
            return None

    def generate_lead_report(self) -> dict:
        """Génère un rapport consolidé en gérant les données manquantes et les valeurs nulles."""
        report = {
            "name": "N/A", "title": "N/A", "company": "N/A",
            "contact_info": {
                "linkedin_profile_url": "N/A", "instagram_username": "N/A", "twitter_username": "N/A"
            },
            "summary": {
                "recent_activity": "N/A", "points_of_interest": [], "potential_pain_points": []
            },
            "social_media_stats": {
                "instagram": {}, "linkedin": {}, "twitter": {}
            },
            "recent_social_activity": {
                "linkedin_posts": [], "twitter_tweets": []
            }
        }

        tavily_data = self._load_json_data("tavily.json")
        if tavily_data:
            report["name"] = tavily_data.get("name") or "N/A"
            report["title"] = tavily_data.get("title") or "N/A"
            if report["title"] != "N/A" and ',' in report["title"]:
                report["company"] = report["title"].split(',')[-1].strip()
            report["summary"]["recent_activity"] = tavily_data.get("recent_activity") or "N/A"
            report["summary"]["points_of_interest"] = tavily_data.get("points_of_interest") or []
            report["summary"]["potential_pain_points"] = tavily_data.get("potential_pain_points") or []
            report["contact_info"]["linkedin_profile_url"] = tavily_data.get("linkedin_profile") or "N/A"

        instagram_data = self._load_json_data("instagram_cleaned.json")
        if instagram_data:
            report["contact_info"]["instagram_username"] = instagram_data.get("username") or "N/A"
            stats = instagram_data.get("stats", {})
            report["social_media_stats"]["instagram"] = {
                "followers": stats.get("followers") or 0,
                "following": stats.get("following") or 0,
                "posts": stats.get("posts") or 0,
                "engagement_rate": stats.get("engagement_rate") or 0.0,
                "category": (instagram_data.get("profile_metadata") or {}).get("category") or "N/A"
            }

        linkedin_posts = self._load_json_data("linkedin_cleaned.json")
        if linkedin_posts:
            total_engagement = sum((p.get("engagement") or {}).get("total", 0) for p in linkedin_posts)
            report["social_media_stats"]["linkedin"] = {
                "total_posts": len(linkedin_posts),
                "total_engagement": total_engagement
            }
            report["recent_social_activity"]["linkedin_posts"] = [
                {"date": p.get("date") or "N/A", "text": p.get("text") or "", "url": p.get("url") or ""}
                for p in linkedin_posts[:3]
            ]

        twitter_tweets = self._load_json_data("twitter_cleaned.json")
        if twitter_tweets:
            stats = {
                "total_likes": sum((t.get("stats") or {}).get("likes", 0) for t in twitter_tweets),
                "total_retweets": sum((t.get("stats") or {}).get("retweets", 0) for t in twitter_tweets),
                "total_replies": sum((t.get("stats") or {}).get("replies", 0) for t in twitter_tweets),
                "total_quotes": sum((t.get("stats") or {}).get("quotes", 0) for t in twitter_tweets),
                "total_views": sum((t.get("stats") or {}).get("views", 0) for t in twitter_tweets)
            }
            report["social_media_stats"]["twitter"] = {"total_tweets": len(twitter_tweets), **stats}
            report["recent_social_activity"]["twitter_tweets"] = [
                {"date": t.get("date") or "N/A", "text": t.get("text") or ""}
                for t in twitter_tweets[:3]
            ]
            if twitter_tweets and "user" in twitter_tweets[0]:
                report["contact_info"]["twitter_username"] = (twitter_tweets[0].get("user") or {}).get("username") or "N/A"
        else:
            report["social_media_stats"]["twitter"] = {
                "total_tweets": 0, "total_likes": 0, "total_retweets": 0, 
                "total_replies": 0, "total_quotes": 0, "total_views": 0
            }

        return report

class EngagementStrategyAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_strategy(self, report_data: dict) -> dict:
        if not self.api_key:
            return {"error": "Erreur: GEMINI_API_KEY non trouvée."}

        prompt = f"""
        En te basant sur le rapport de lead suivant, génère deux choses :
        1. Un rapport de synthèse en Markdown, concis et actionnable pour une équipe commerciale.
        2. Un objet JSON qui réplique la structure du rapport de lead fourni, en remplissant les valeurs.

        Rapport de Lead (JSON brut):
        {json.dumps(report_data, indent=2, ensure_ascii=False)}

        Réponds UNIQUEMENT avec un objet JSON valide qui a la structure suivante :
        {{
          "markdown_report": "...",
          "json_report": {json.dumps(report_data, indent=2, ensure_ascii=False)}
        }}
        """

        try:
            # Configure le modèle pour qu'il retourne du JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            # Essayer de nettoyer et parser la réponse JSON
            # Le modèle peut parfois retourner le JSON dans un bloc de démarquage
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
            
            return json.loads(cleaned_response_text)
        except (json.JSONDecodeError, Exception) as e:
            error_message = f"Erreur lors de la génération ou du parsing de la réponse JSON de Gemini: {e}"
            print(error_message)
            # Retourner une structure d'erreur cohérente
            return {
                "error": error_message,
                "markdown_report": "Génération du rapport échouée.",
                "json_report": {"name": "error", "company_name": "error", "linkedin_profile": "error"}
            }
