import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class TwitterCleaner:
    @staticmethod
    def clean(raw_data: str) -> List[Dict[str, Any]]:
        """
        Nettoie les données brutes Twitter et retourne un format simplifié
        :param raw_data: Données brutes au format JSON
        :return: Liste de tweets structurés
        """
        try:
            data = json.loads(raw_data)
            # Vérifie si "timeline" existe, sinon utilise la racine comme liste
            tweets = data.get("timeline", [])
            if not isinstance(tweets, list):
                tweets = [tweets]  # Si ce n'est pas une liste, on la crée
            
            cleaned_tweets = []
            for tweet in tweets:
                try:
                    cleaned_tweet = TwitterCleaner._simplify_tweet(tweet)
                    cleaned_tweets.append(cleaned_tweet)
                except Exception as e:
                    print(f"⚠️ Erreur lors du nettoyage d'un tweet: {e}")
                    continue
            
            return cleaned_tweets
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur de décodage JSON: {e}")
            return []
        except Exception as e:
            print(f"⚠️ Erreur inattendue: {e}")
            return []

    @staticmethod
    def _simplify_tweet(tweet: Dict[str, Any]) -> Dict[str, Any]:
        """Simplifie radicalement la structure d'un tweet"""
        return {
            "id": tweet.get("tweet_id", ""),
            "type": TwitterCleaner._get_tweet_type(tweet),
            "date": tweet.get("created_at", ""),
            "text": TwitterCleaner._clean_text(tweet.get("text", "")),
            "author": TwitterCleaner._simplify_author(tweet.get("author", {})),
            "stats": TwitterCleaner._simplify_stats(tweet),
            "has_media": bool(tweet.get("media")),
            "is_retweet": "retweeted" in tweet,
            "is_quote": "quoted" in tweet
        }

    # @staticmethod
    # def _get_tweet_url(tweet: Dict[str, Any]) -> str:
    #     """Construit l'URL du tweet si absente"""
    #     if "url" in tweet:
    #         return tweet["url"]
    #     author = tweet.get("author", {})
    #     return f"https://twitter.com/{author.get('screen_name', '')}/status/{tweet.get('tweet_id', '')}"

    @staticmethod
    def _get_tweet_type(tweet: Dict[str, Any]) -> str:
        """Détermine le type de tweet"""
        if "retweeted" in tweet:
            return "retweet"
        if "quoted" in tweet:
            return "quote"
        return "original"

    @staticmethod
    def _clean_text(text: str) -> str:
        """Nettoie le texte du tweet"""
        return " ".join(text.split()).strip() if text else ""

    @staticmethod
    def _simplify_author(author: Dict[str, Any]) -> Dict[str, str]:
        """Simplifie les infos auteur"""
        return {
            "name": author.get("name", ""),
        }

    @staticmethod
    def _simplify_stats(tweet: Dict[str, Any]) -> Dict[str, int]:
        """Simplifie les statistiques"""
        return {
            "likes": tweet.get("favorites", 0),
            "retweets": tweet.get("retweets", 0),
            "replies": tweet.get("replies", 0),
            "quotes": tweet.get("quotes", 0),
            "views": int(tweet.get("views", 0)) if tweet.get("views") else 0
        }

# Exemple d'utilisation
# if __name__ == "__main__":
#     # Lecture du fichier
#     try:
#         with open("data/Talan/ImenAyari/twitter.txt", "r", encoding="utf-8") as file:
#             raw_data = file.read()
        
#         # Nettoyage des données
#         cleaned_data = TwitterCleaner.clean(raw_data)
        
#         # Vérification du résultat
#         print(f"Nombre de tweets nettoyés: {len(cleaned_data)}")
#         if cleaned_data:
#             print("Exemple de tweet nettoyé:")
#             print(json.dumps(cleaned_data[0], indent=2, ensure_ascii=False))
            
#             # Sauvegarde dans un fichier
#             with open("twitter_cleaned.json", "w", encoding="utf-8") as out_file:
#                 json.dump(cleaned_data, out_file, indent=2, ensure_ascii=False)
#     except FileNotFoundError:
#         print("⚠️ Fichier twitter.txt introuvable")
#     except Exception as e:
#         print(f"⚠️ Erreur lors de la lecture du fichier: {e}")