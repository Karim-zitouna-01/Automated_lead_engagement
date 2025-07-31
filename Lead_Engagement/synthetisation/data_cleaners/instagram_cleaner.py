import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class InstagramCleaner:
    @staticmethod
    def clean(raw_data: str) -> Dict[str, Any]:
        """
        Nettoie les données brutes Instagram et retourne un format structuré
        :param raw_data: Données brutes au format texte (fichier .txt)
        :return: Dictionnaire structuré pour analyse LLM
        """
        try:
            # Étape 1: Conversion du texte brut en dictionnaire
            parsed_data = InstagramCleaner._parse_raw_text(raw_data)
            
            # Étape 2: Construction de la structure de sortie
            cleaned = {
                "platform": "instagram",
                "username": InstagramCleaner._safe_get_str(parsed_data, "username"),
                "full_name": InstagramCleaner._safe_get_str(parsed_data, "full_name"),
                "is_private": InstagramCleaner._safe_get_bool(parsed_data, "is_private"),
                "pk": InstagramCleaner._safe_get_str(parsed_data, "pk"),
                "bio": InstagramCleaner._clean_bio(parsed_data.get("biography_with_entities", "")),
                "stats": {
                    "followers": InstagramCleaner._safe_get_int(parsed_data, "follower_count"),
                    "following": InstagramCleaner._safe_get_int(parsed_data, "following_count"),
                    "posts": InstagramCleaner._safe_get_int(parsed_data, "media_count"),
                    "engagement_rate": InstagramCleaner._calculate_engagement(parsed_data),
                    "igtv_videos": InstagramCleaner._safe_get_int(parsed_data, "total_igtv_videos"),
                    "clips": InstagramCleaner._safe_get_int(parsed_data, "total_clips_count")
                },
                "profile_metadata": {
                    "is_verified": InstagramCleaner._safe_get_bool(parsed_data, "is_verified"),
                    "category": InstagramCleaner._safe_get_str(parsed_data, "category"),
                    "category_id": InstagramCleaner._safe_get_int(parsed_data, "category_id"),
                    "profile_pic_url": InstagramCleaner._safe_get_str(parsed_data, "profile_pic_url"),
                    "hd_profile_pic_url": InstagramCleaner._get_hd_profile_url(parsed_data),
                    "hd_profile_pic_versions": InstagramCleaner._get_profile_pic_versions(parsed_data)
                },
                "account_info": {
                    "account_type": InstagramCleaner._safe_get_int(parsed_data, "account_type"),
                    "is_eligible_for_smb_support_flow": InstagramCleaner._safe_get_bool(parsed_data, "is_eligible_for_smb_support_flow"),
                    "business_contact_method": InstagramCleaner._safe_get_str(parsed_data, "business_contact_method"),
                    "page_id": InstagramCleaner._safe_get_str(parsed_data, "page_id"),
                    "page_name": InstagramCleaner._safe_get_str(parsed_data, "page_name"),
                    "has_highlight_reels": InstagramCleaner._safe_get_bool(parsed_data, "has_highlight_reels"),
                    "has_videos": InstagramCleaner._safe_get_bool(parsed_data, "has_videos"),
                    "has_chaining": InstagramCleaner._safe_get_bool(parsed_data, "has_chaining"),
                    "has_private_collections": InstagramCleaner._safe_get_bool(parsed_data, "has_private_collections")
                }
            }
            
            return cleaned
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
            return {}

    @staticmethod
    def _parse_raw_text(raw_text: str) -> Dict[str, Any]:
        """Convertit le texte brut en dictionnaire structuré"""
        result = {}
        current_key = None
        current_value = []
        
        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                if current_key:
                    value = '\n'.join(current_value).strip()
                    result[current_key] = InstagramCleaner._convert_value(value)
                    current_value = []
                
                key, _, value = line.partition(':')
                current_key = key.strip()
                value = value.strip().strip('"')  # Supprime les guillemets
                
                if value:
                    current_value.append(value)
            elif current_key:
                current_value.append(line)
        
        if current_key:
            value = '\n'.join(current_value).strip()
            result[current_key] = InstagramCleaner._convert_value(value)
        
        # Traitement spécial pour les structures imbriquées
        if "hd_profile_pic_url_info" in result:
            try:
                result["hd_profile_pic_url_info"] = json.loads(result["hd_profile_pic_url_info"])
            except:
                pass
                
        if "hd_profile_pic_versions" in result:
            try:
                result["hd_profile_pic_versions"] = json.loads(result["hd_profile_pic_versions"])
            except:
                pass
                
        return result

    @staticmethod
    def _convert_value(value: str) -> Any:
        """Convertit automatiquement les types de valeurs"""
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
            return float(value)
        elif value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except:
                return value
        return value

    @staticmethod
    def _safe_get_str(data: Dict[str, Any], key: str) -> str:
        """Récupère une valeur string de manière sécurisée"""
        value = data.get(key, "")
        return str(value) if value is not None else ""

    @staticmethod
    def _safe_get_int(data: Dict[str, Any], key: str) -> int:
        """Récupère une valeur int de manière sécurisée"""
        try:
            value = data.get(key, 0)
            return int(value) if value is not None else 0
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _safe_get_bool(data: Dict[str, Any], key: str) -> bool:
        """Récupère une valeur booléenne de manière sécurisée"""
        value = data.get(key, False)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)

    @staticmethod
    def _get_hd_profile_url(data: Dict[str, Any]) -> str:
        """Récupère l'URL HD de la photo de profil"""
        if "hd_profile_pic_url_info" in data and isinstance(data["hd_profile_pic_url_info"], dict):
            return data["hd_profile_pic_url_info"].get("url", "")
        return ""

    @staticmethod
    def _get_profile_pic_versions(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Récupère les différentes versions de la photo de profil"""
        versions = []
        if "hd_profile_pic_versions" in data and isinstance(data["hd_profile_pic_versions"], list):
            for version in data["hd_profile_pic_versions"]:
                if isinstance(version, dict):
                    versions.append({
                        "width": version.get("width", 0),
                        "height": version.get("height", 0),
                        "url": version.get("url", "")
                    })
        return versions

    @staticmethod
    def _clean_bio(raw_bio: str) -> str:
        """Nettoie la biographie et extrait le texte utile"""
        if not raw_bio:
            return ""
        
        # Extraction du texte brut si format JSON
        if raw_bio.startswith('{'):
            try:
                bio_data = json.loads(raw_bio)
                return bio_data.get("raw_text", "")
            except:
                pass
        
        # Nettoyage de base
        return re.sub(r'\s+', ' ', raw_bio).strip()

    @staticmethod
    def _calculate_engagement(data: Dict[str, Any]) -> float:
        """Calcule le taux d'engagement approximatif"""
        try:
            followers = InstagramCleaner._safe_get_int(data, "follower_count")
            if followers <= 0:
                return 0.0
            
            total_likes = 0
            total_posts = 0
            
            if "recent_media" in data and isinstance(data["recent_media"], list):
                for post in data["recent_media"][:9]:  # 9 derniers posts max
                    if isinstance(post, dict):
                        total_likes += InstagramCleaner._safe_get_int(post, "like_count")
                        total_posts += 1
            
            if total_posts == 0:
                return 0.0
                
            avg_likes = total_likes / total_posts
            return round((avg_likes / followers) * 100, 2)
        except Exception as e:
            print(f"⚠️ Erreur dans le calcul d'engagement: {e}")
            return 0.0

