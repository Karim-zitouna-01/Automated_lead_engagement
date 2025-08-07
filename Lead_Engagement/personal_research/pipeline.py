

import json
import os
import re
from typing import List, Dict, Any, Optional, TypedDict

# --- Dépendances externes (à installer) ---
import google.generativeai as genai
from dotenv import load_dotenv
from apify_client import ApifyClient
import http.client
from tavily import TavilyClient

# --- Configuration initiale ---
load_dotenv()

# Clés API
APIFY_KEY = os.getenv("APIFY_KEY", "apify_api_8Tshzy61AFMoqcD9O2fnxODpgAH9CK4oDuVu")
RAPID_API_KEY = os.getenv("RAPID_API_KEY", "30f0a8d6e4msh13d82afdd7da410p195c0ejsn41d7f2805fb1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Configuration des clients
genai.configure(api_key=GEMINI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
llm = genai.GenerativeModel('models/gemini-1.5-flash')


# ==============================================================================
# SECTION 1 : FONCTIONS DE COLLECTE DE DONNÉES (depuis social_media.py et tavily_searcher.py)
# ==============================================================================

class KeyPersonnel(TypedDict):
    name: str
    title: str
    linkedin_profile: Optional[str]
    recent_activity: Optional[str]
    points_of_interest: Optional[List[str]]
    potential_pain_points: Optional[List[str]]

def get_enriched_personnel_profiles(
    personnel_list: List[Dict[str, Any]],
    company_name: str,
    icp: Dict[str, Any]
) -> List[KeyPersonnel]:
    """Enrichit les profils via Tavily et Gemini."""
    enriched_personnel_list: List[KeyPersonnel] = []
    for person in personnel_list:
        name = person.get("name")
        if not name:
            continue
        
        enriched: KeyPersonnel = {
            "name": name,
            "title": person.get("title"),
            "linkedin_profile": person.get("linkedin_profile"),
            "recent_activity": "No specific recent activity found.",
            "points_of_interest": [],
            "potential_pain_points": []
        }
        
        queries = [
            f'recent articles or interviews by "{name}" "{company_name}"',
            f'"{name}" "{company_name}" professional focus priorities',
            f'linkedin posts by "{name}" on challenges in the {icp.get("industry", {}).get("tier1_core_focus",[None])[0]} sector'
        ]
        
        context = ""
        for q in queries:
            try:
                resp = tavily_client.search(query=q, search_depth="advanced", max_results=2)
                context += "\n".join([res.get("content","") for res in resp.get("results", [])]) + "\n"
            except Exception as e:
                print(f"Erreur lors de la recherche Tavily pour la requête '{q}': {e}")

        if context.strip():
            prompt = f"""
Based on the following information about {name}, {enriched['title']} at {company_name}, and ICP pain points: {', '.join(icp.get('pain_points',[]))}:

Research context:
---
{context}
---

Please return a JSON object with:
{{
  "recent_activity": "...",
  "points_of_interest": ["...", "..."],
  "potential_pain_points": ["...", "..."]
}}
"""
            try:
                resp = llm.generate_content(prompt)
                text = resp.text.strip()
                js_start = text.find("{")
                js_end = text.rfind("}")
                if js_start != -1 and js_end != -1:
                    parsed = json.loads(text[js_start:js_end+1])
                    enriched.update(parsed)
            except Exception as e:
                print(f"Erreur lors de l'appel à Gemini pour {name}: {e}")

        enriched_personnel_list.append(enriched)
    return enriched_personnel_list

def linkedinsearch(username):
    """Recherche sur LinkedIn via Apify."""
    if not username: return None
    try:
        client = ApifyClient(APIFY_KEY)
        run_input = {"username": f"{username}", "page_number": 1, "limit": 5}
        run = client.actor("LQQIXN9Othf8f7R5n").call(run_input=run_input)
        return [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
    except Exception as e:
        print(f"Erreur Apify (LinkedIn) pour {username}: {e}")
        return None

def twittersearch(username):
    """Recherche sur Twitter via RapidAPI."""
    if not username: return None
    try:
        conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
        headers = {'x-rapidapi-key': RAPID_API_KEY, 'x-rapidapi-host': "twitter-api45.p.rapidapi.com"}
        conn.request("GET", f"/timeline.php?screenname={username}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Erreur RapidAPI (Twitter) pour {username}: {e}")
        return None

def instasearch(username):
    """Recherche sur Instagram via RapidAPI."""
    if not username: return None
    try:
        conn = http.client.HTTPSConnection("instagram-api-fast-reliable-data-scraper.p.rapidapi.com")
        headers = {'x-rapidapi-key': RAPID_API_KEY, 'x-rapidapi-host': "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"}
        conn.request("GET", f"/profile?username={username}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Erreur RapidAPI (Instagram) pour {username}: {e}")
        return None

def search_all_socials(linkedin_username, twitter_username, insta_username):
    """Lance toutes les recherches sur les réseaux sociaux."""
    return {
        "linkedin": linkedinsearch(linkedin_username),
        "twitter": twittersearch(twitter_username),
        "instagram": instasearch(insta_username)
    }

# ==============================================================================
# SECTION 2 : FONCTIONS DE TRANSFORMATION (depuis new.py)
# ==============================================================================

def get_nested_value(data, path):
    """Récupère une valeur imbriquée dans un dictionnaire."""
    keys = path.split('.')
    current_value = data
    for key in keys:
        if isinstance(current_value, dict) and key in current_value:
            current_value = current_value[key]
        elif isinstance(current_value, list) and key.isdigit():
            try:
                current_value = current_value[int(key)]
            except (IndexError, ValueError):
                return None
        else:
            return None
    return current_value

def transform_data(source_data, template_data, mapping_config):
    """Mappe et transforme les données brutes vers le format final."""
    output_data = json.loads(json.dumps(template_data)) # Deep copy

    for target_path, source_rule in mapping_config.items():
        target_keys = target_path.split('.')
        current_output_level = output_data
        
        for i, key in enumerate(target_keys[:-1]):
            current_output_level = current_output_level.setdefault(key, {})

        target_key = target_keys[-1]

        value = None
        if isinstance(source_rule, str):
            value = get_nested_value(source_data, source_rule)
        elif isinstance(source_rule, dict):
            source_path = source_rule.get("source")
            rule_type = source_rule.get("type")
            source_value = get_nested_value(source_data, source_path) if source_path else None

            if rule_type == "count" and isinstance(source_value, list):
                value = len(source_value)
            elif rule_type == "sum_field" and isinstance(source_value, list):
                field_to_sum = source_rule.get("field")
                if field_to_sum:
                    value = sum(get_nested_value(item, field_to_sum) or 0 for item in source_value)
            elif rule_type == "list_transform" and isinstance(source_value, list):
                limit = source_rule.get("limit")
                fields_map = source_rule.get("fields", {})
                transformed_list = []
                for item in source_value[:limit]:
                    transformed_item = {new_field: get_nested_value(item, old_path) for new_field, old_path in fields_map.items()}
                    transformed_list.append(transformed_item)
                value = transformed_list
            elif target_path == "company" and source_value:
                 match = re.search(r',\s*(.+)', source_value)
                 value = match.group(1).strip() if match else source_value.split()[-1]

        if value is not None:
            current_output_level[target_key] = value

    if not output_data.get("contact_info", {}).get("linkedin_profile_url"):
        linkedin_username = get_nested_value(source_data, "linkedin.0.author.username")
        if linkedin_username:
            output_data["contact_info"]["linkedin_profile_url"] = f"https://www.linkedin.com/in/{linkedin_username}"
            
    return output_data

def enrich_with_gemini_final(data_to_enrich):
    """Génère la description de l'entreprise avec Gemini."""
    company_name = data_to_enrich.get("company", "")
    if not company_name:
        return data_to_enrich

    recent_activity = data_to_enrich.get("summary", {}).get("recent_activity", "")
    points_of_interest = "; ".join(data_to_enrich.get("summary", {}).get("points_of_interest", []))

    prompt = f"""En tant qu'expert en communication d'entreprise, rédigez une description concise et percutante de l'entreprise {company_name} en vous basant sur les informations suivantes :
Activité récente : {recent_activity}
Points d'intérêt : {points_of_interest}
La description doit être professionnelle, informative et ne pas dépasser 3 phrases."""

    try:
        response = llm.generate_content(prompt)
        data_to_enrich["company_description"] = response.text.strip()
    except Exception as e:
        print(f"Erreur lors de la génération de la description de l'entreprise : {e}")
        data_to_enrich["company_description"] = "Description non disponible."
        
    return data_to_enrich

# ==============================================================================
# SECTION 3 : FONCTION PRINCIPALE DU PIPELINE
# ==============================================================================

def process_lead_pipeline(
    personnel_list: List[Dict[str, Any]],
    company_name: str,
    icp: Dict[str, Any],
    usernames_list: List[Dict[str, Any]],
    template_path: str,
    mapping_config_path: str
) -> List[Dict[str, Any]]:
    """
    Exécute le pipeline complet de traitement de leads en mémoire.
    
    Args:
        personnel_list: Liste des personnes avec nom et titre.
        company_name: Nom de l'entreprise cible.
        icp: Profil du client idéal (Ideal Customer Profile).
        usernames_list: Liste des personnes avec leurs pseudos sur les réseaux sociaux.
        template_path: Chemin vers le fichier JSON modèle pour la sortie.
        mapping_config_path: Chemin vers le fichier de configuration du mappage.

    Returns:
        Une liste de dictionnaires, chaque dictionnaire étant un profil traité.
    """
    print("--- Démarrage du pipeline de traitement de leads ---")

    # 1. Charger les configurations une seule fois
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        with open(mapping_config_path, 'r', encoding='utf-8') as f:
            mapping_config = json.load(f)
    except FileNotFoundError as e:
        print(f"Erreur: Fichier de configuration introuvable - {e}")
        return []
    
    # 2. Enrichissement initial avec Tavily
    print("Étape 1/4 : Enrichissement des profils avec Tavily...")
    tavily_enriched_profiles = get_enriched_personnel_profiles(personnel_list, company_name, icp)
    
    final_processed_profiles = []

    # 3. Traiter chaque personne
    for person_socials in usernames_list:
        name = person_socials.get("name")
        if not name:
            continue
            
        print(f"\n--- Traitement de : {name} ---")

        # Trouver le profil Tavily correspondant
        tavily_profile = next((p for p in tavily_enriched_profiles if p.get("name") == name), None)
        if not tavily_profile:
            print(f"Aucun profil enrichi trouvé pour {name}, passage au suivant.")
            continue

        # 4. Recherche sur les réseaux sociaux
        print(f"Étape 2/4 : Recherche de {name} sur les réseaux sociaux...")
        social_data = search_all_socials(
            person_socials.get("linkedin_profile"),
            person_socials.get("twitter_profile"),
            person_socials.get("instagram_profile")
        )

        # 5. Combinaison des données brutes
        raw_profile_data = {
            "tavily": tavily_profile,
            **social_data
        }

        # 6. Transformation des données
        print(f"Étape 3/4 : Transformation des données pour {name}...")
        transformed_data = transform_data(raw_profile_data, template_data, mapping_config)

        # 7. Enrichissement final avec Gemini
        print(f"Étape 4/4 : Enrichissement final pour {name} avec Gemini...")
        final_data = enrich_with_gemini_final(transformed_data)
        
        # 8. Ajout du profil traité à la liste finale
        final_processed_profiles.append(final_data)
        print(f"✅ Profil traité pour {name} ajouté aux résultats.")

    print("\n--- Pipeline terminé ---")
    return final_processed_profiles


# ==============================================================================
# SECTION 4 : EXEMPLE D'UTILISATION
# ==============================================================================

if __name__ == "__main__":
    # Définition des entrées (similaire à engament_01.py)
    personnel_list_input = [
        {"name": "Thierry Millet", "title": "CEO, Orange Tunisie", "linkedin_profile": None},
    ]
    company_name_input = "Orange Tunisie"
    icp_input = {
        "industry": {"tier1_core_focus": ["digital transformation", "telecom services"]},
        "pain_points": ["digital adoption among SMEs", "cybersecurity services uptake", "start-up acceleration"]
    }
    usernames_list_input = [
        {"name": "Thierry Millet", "linkedin_profile": "thierry-millet-b60809b3",
         "twitter_profile": "millet_thierryr",
         "instagram_profile": "thierry.millet64"},
    ]

    # Définition des chemins de configuration (similaire à new.py)
    # Utilisation de os.path.join pour la compatibilité entre OS
    base_dir = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_PATH = os.path.join(base_dir, "profiles", "json_example.json")
    MAPPING_CONFIG_PATH = os.path.join(base_dir, "profiles", "mapping_config.json")

    # Appel de la fonction pipeline
    processed_profiles = process_lead_pipeline(
        personnel_list=personnel_list_input,
        company_name=company_name_input,
        icp=icp_input,
        usernames_list=usernames_list_input,
        template_path=TEMPLATE_PATH,
        mapping_config_path=MAPPING_CONFIG_PATH
    )

    # Afficher le résultat final
    print("\n--- Résultat final du pipeline ---")
    print(json.dumps(processed_profiles, indent=2, ensure_ascii=False))


