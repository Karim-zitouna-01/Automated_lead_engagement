import json
from typing import Dict, Any, List, Optional

class LinkedInCleaner:
    @staticmethod
    def clean(raw_data: str) -> List[Dict[str, Any]]:
        """
        Nettoie les données brutes LinkedIn et retourne un format simplifié
        :param raw_data: Données brutes au format JSON
        :return: Liste de posts simplifiés
        """
        try:
            posts_data = json.loads(raw_data)
            return [LinkedInCleaner._simplify_post(post) for post in posts_data]
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
            return []

    @staticmethod
    def _simplify_post(post: Dict[str, Any]) -> Dict[str, Any]:
        """Simplifie radicalement la structure d'un post"""
        return {
            "id": post.get("urn", ""),
            "type": post.get("post_type", ""),
            "date": post.get("posted_at", {}).get("date", ""),
            "text": LinkedInCleaner._clean_text(post.get("text", "")),
            "author": LinkedInCleaner._simplify_author(post.get("author", {})),
            "engagement": LinkedInCleaner._simplify_stats(post.get("stats", {})),
            "has_media": bool(post.get("media")),
            "is_reshare": bool(post.get("reshared_post"))
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Nettoie le texte du post"""
        return " ".join(text.split()).strip() if text else ""

    @staticmethod
    def _simplify_author(author: Dict[str, Any]) -> Dict[str, str]:
        """Simplifie les infos auteur"""
        return {
            "name": f"{author.get('first_name', '')} {author.get('last_name', '')}".strip(),
           
        }

    @staticmethod
    def _simplify_stats(stats: Dict[str, Any]) -> Dict[str, int]:
        """Simplifie les statistiques"""
        return {
            "total": stats.get("total_reactions", 0),
            "comments": stats.get("comments", 0),
            "shares": stats.get("reposts", 0)
        }