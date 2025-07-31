import json
import os
import google.generativeai as genai

class DataConsolidationAgent:
    def __init__(self, lead_data_path: str):
        self.lead_data_path = lead_data_path

    def generate_lead_report(self) -> dict:
        report = {
            "name": None,
            "title": None,
            "company": None,
            "contact_info": {
                "linkedin_profile_url": None,
                "instagram_username": None,
                "twitter_username": None
            },
            "summary": {
                "recent_activity": None,
                "points_of_interest": [],
                "potential_pain_points": []
            },
            "social_media_stats": {
                "instagram": {},
                "linkedin": {},
                "twitter": {}
            },
            "recent_social_activity": {
                "linkedin_posts": [],
                "twitter_tweets": []
            }
        }

        # Charger les données Tavily (informations principales)
        tavily_path = os.path.join(self.lead_data_path, "tavily.json")
        if os.path.exists(tavily_path):
            with open(tavily_path, 'r', encoding='utf-8') as f:
                tavily_data = json.load(f)
                report["name"] = tavily_data.get("name")
                report["title"] = tavily_data.get("title")
                if report["title"] and "Talan Tunisie" in report["title"]:
                    report["company"] = "Talan Tunisie"
                report["summary"]["recent_activity"] = tavily_data.get("recent_activity")
                report["summary"]["points_of_interest"] = tavily_data.get("points_of_interest", [])
                report["summary"]["potential_pain_points"] = tavily_data.get("potential_pain_points", [])
                if tavily_data.get("linkedin_profile"):
                    report["contact_info"]["linkedin_profile_url"] = tavily_data["linkedin_profile"]

        # Charger les données Instagram
        instagram_path = os.path.join(self.lead_data_path, "instagram_cleaned.json")
        if os.path.exists(instagram_path):
            with open(instagram_path, 'r', encoding='utf-8') as f:
                instagram_data = json.load(f)
                report["contact_info"]["instagram_username"] = instagram_data.get("username")
                report["social_media_stats"]["instagram"] = {
                    "followers": instagram_data.get("stats", {}).get("followers"),
                    "following": instagram_data.get("stats", {}).get("following"),
                    "posts": instagram_data.get("stats", {}).get("posts"),
                    "engagement_rate": instagram_data.get("stats", {}).get("engagement_rate"),
                    "category": instagram_data.get("profile_metadata", {}).get("category")
                }

        # Charger les données LinkedIn
        linkedin_path = os.path.join(self.lead_data_path, "linkedin_cleaned.json")
        if os.path.exists(linkedin_path):
            with open(linkedin_path, 'r', encoding='utf-8') as f:
                linkedin_posts = json.load(f)
                total_engagement = 0
                for post in linkedin_posts:
                    total_engagement += post.get("engagement", {}).get("total", 0)
                report["social_media_stats"]["linkedin"] = {
                    "total_posts": len(linkedin_posts),
                    "total_engagement": total_engagement
                }
                report["recent_social_activity"]["linkedin_posts"] = [
                    {"date": p.get("date"), "text": p.get("text"), "url": p.get("url")}
                    for p in linkedin_posts[:3]
                ]

        # Charger les données Twitter
        twitter_path = os.path.join(self.lead_data_path, "twitter_cleaned.json")
        if os.path.exists(twitter_path):
            with open(twitter_path, 'r', encoding='utf-8') as f:
                twitter_tweets = json.load(f)
                total_likes = 0
                total_retweets = 0
                total_replies = 0
                total_quotes = 0
                total_views = 0
                for tweet in twitter_tweets:
                    total_likes += tweet.get("stats", {}).get("likes", 0)
                    total_retweets += tweet.get("stats", {}).get("retweets", 0)
                    total_replies += tweet.get("stats", {}).get("replies", 0)
                    total_quotes += tweet.get("stats", {}).get("quotes", 0)
                    total_views += tweet.get("stats", {}).get("views", 0)
                report["social_media_stats"]["twitter"] = {
                    "total_tweets": len(twitter_tweets),
                    "total_likes": total_likes,
                    "total_retweets": total_retweets,
                    "total_replies": total_replies,
                    "total_quotes": total_quotes,
                    "total_views": total_views
                }
                report["recent_social_activity"]["twitter_tweets"] = [
                    {"date": t.get("date"), "text": t.get("text")}
                    for t in twitter_tweets[:3]
                ]
        
        return report

class EngagementStrategyAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_strategy(self, report_data: dict) -> str:
        if not self.api_key:
            return "Erreur: GEMINI_API_KEY non trouvée."

        if not self.api_key:
            return "Erreur: GEMINI_API_KEY non trouvée."

        prompt = f"""
        Synthétise le rapport de lead suivant en un résumé concis et actionnable pour une équipe commerciale. 
        Mets en évidence les points clés, les centres d'intérêt, les points de douleur potentiels et les informations pertinentes sur les réseaux sociaux. 
        Le résumé doit être direct et utile pour engager le lead. 
        
        Rapport de Lead (JSON):
        {json.dumps(report_data, indent=2, ensure_ascii=False)}
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la génération de la synthèse avec Gemini: {e}"
