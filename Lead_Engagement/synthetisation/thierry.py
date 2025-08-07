'''
Ce script transforme les données d'un profil JSON brut (Thierry_Millet.json) 
en une structure JSON normalisée (selon json_example.json), 
enrichit les données avec l'API Gemini, et sauvegarde le résultat.
'''

import json
import os
import re
import google.generativeai as genai
# Importer une bibliothèque pour charger les variables d'environnement si nécessaire, ex: python-dotenv
from dotenv import load_dotenv

# Charger les variables d'environnement (si vous utilisez un fichier .env)
load_dotenv()

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
     
SOURCE_FILE_PATH = r"C:\Users\yaola\Videos\formation_2025\Agentic_ai\Automated_lead_engagement\Lead_Engagement\personal_research\profiles\Thierry_Millet.json"

TEMPLATE_FILE_PATH = r"C:\Users\yaola\Videos\formation_2025\Agentic_ai\Automated_lead_engagement\Lead_Engagement\personal_research\profiles\json_example.json"

OUTPUT_FILE_PATH = "Thierry_Millet_processed.json"
MAPPING_CONFIG_FILE = r"C:\Users\yaola\Videos\formation_2025\Agentic_ai\Automated_lead_engagement\Lead_Engagement\personal_research\profiles\mapping_config.json"

# --- FONCTIONS ---

def read_json_file(file_path):
    '''Charge et retourne le contenu d'un fichier JSON.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} n'a pas été trouvé.")
        return None
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {file_path} n'est pas un JSON valide.")
        return None

def get_nested_value(data, path):
    """Récupère une valeur imbriquée dans un dictionnaire en utilisant un chemin pointé.
    Ex: get_nested_value(data, 'tavily.name')
    """
    keys = path.split('.')
    current_value = data
    for key in keys:
        if isinstance(current_value, dict) and key in current_value:
            current_value = current_value[key]
        elif isinstance(current_value, list) and key.isdigit(): # Handle list indices
            try:
                current_value = current_value[int(key)]
            except (IndexError, ValueError):
                return None
        else:
            return None
    return current_value

def transform_data(source_data, template_data, mapping_config):
    '''Mappe et transforme les données de la source vers le modèle en utilisant la configuration de mappage.'''
    print("Début de la transformation des données...")
    
    output_data = json.loads(json.dumps(template_data))

    for target_path, source_rule in mapping_config.items():
        target_keys = target_path.split('.')
        current_output_level = output_data

        # Naviguer jusqu'au niveau parent du chemin cible
        for i, key in enumerate(target_keys):
            if i == len(target_keys) - 1: # Dernier élément, c'est la clé cible
                break
            if key not in current_output_level or not isinstance(current_output_level[key], (dict, list)):
                # Créer un dictionnaire si le chemin n'existe pas ou n'est pas un conteneur
                current_output_level[key] = {}
            current_output_level = current_output_level[key]

        target_key = target_keys[-1]

        if isinstance(source_rule, str): # Mappage direct
            value = get_nested_value(source_data, source_rule)
            if value is not None:
                current_output_level[target_key] = value
        elif isinstance(source_rule, dict): # Règles complexes
            source_path = source_rule.get("source")
            rule_type = source_rule.get("type")

            if rule_type == "count":
                list_data = get_nested_value(source_data, source_path)
                if isinstance(list_data, list):
                    current_output_level[target_key] = len(list_data)
            elif rule_type == "sum_field":
                list_data = get_nested_value(source_data, source_path)
                field_to_sum = source_rule.get("field")
                if isinstance(list_data, list) and field_to_sum:
                    total_sum = sum(get_nested_value(item, field_to_sum) or 0 for item in list_data)
                    current_output_level[target_key] = total_sum
            elif rule_type == "list_transform":
                list_data = get_nested_value(source_data, source_path)
                limit = source_rule.get("limit")
                fields_map = source_rule.get("fields", {})
                
                transformed_list = []
                if isinstance(list_data, list):
                    for item in list_data[:limit]:
                        transformed_item = {}
                        for new_field, old_field_path in fields_map.items():
                            transformed_item[new_field] = get_nested_value(item, old_field_path)
                        transformed_list.append(transformed_item)
                current_output_level[target_key] = transformed_list
            elif target_path == "company" and source_rule.get("source"): # Règle d'extraction dynamique pour le champ company
                source_value = get_nested_value(source_data, source_rule.get("source"))
                if source_value:
                    company_name = ""
                    # Try to extract company after ", "
                    match = re.search(r',\s*(.+)', source_value)
                    if match:
                        company_name = match.group(1).strip()
                    else:
                        # Fallback: if no comma, try to extract the last significant word/phrase
                        words = source_value.split()
                        if len(words) > 0:
                            company_name = words[-1] # Last word as a fallback
                    current_output_level[target_key] = company_name
            elif source_rule.get("extract_regex"): # Règle d'extraction par regex (pour d'autres champs si nécessaire)
                source_value = get_nested_value(source_data, source_path)
                regex = source_rule.get("extract_regex")
                if source_value and regex and re.search(regex, source_value): # Use re.search for regex matching
                    current_output_level[target_key] = re.search(regex, source_value).group(0) # Extract the matched part

    # Cas spécifique pour linkedin_profile_url si null dans tavily mais présent dans linkedin
    if not output_data["contact_info"]["linkedin_profile_url"]:
        linkedin_username = get_nested_value(source_data, "linkedin.0.author.username")
        if linkedin_username:
            output_data["contact_info"]["linkedin_profile_url"] = f"https://www.linkedin.com/in/{linkedin_username}"

    print("Transformation terminée.")
    return output_data

def enrich_with_gemini(data_to_enrich):
    '''Enrichit les données en utilisant l'API Gemini.'''
    print("Début de l'enrichissement avec Gemini...")
    
    company_name = data_to_enrich.get("company", "")
    recent_activity = data_to_enrich.get("summary", {}).get("recent_activity", "")
    points_of_interest = "; ".join(data_to_enrich.get("summary", {}).get("points_of_interest", []))

    if not company_name:
        print("Nom de l'entreprise non trouvé, impossible d'enrichir avec Gemini.")
        return data_to_enrich

    prompt = f"""En tant qu'expert en communication d'entreprise, rédigez une description concise et percutante de l'entreprise {company_name} en vous basant sur les informations suivantes :

Activité récente : {recent_activity}
Points d'intérêt : {points_of_interest}

La description doit être professionnelle, informative et ne pas dépasser 3 phrases. Elle doit mettre en avant la mission et les réalisations clés de l'entreprise."""

    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        company_description = response.text.strip()
        data_to_enrich["company_description"] = company_description
        print("Description de l'entreprise générée avec succès par Gemini.")
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Gemini : {e}")

    print("Enrichissement terminé.")
    return data_to_enrich # Retourne les données enrichies

def write_json_file(data, file_path):
    '''Écrit les données dans un fichier JSON.'''
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Le fichier de sortie a été créé avec succès : {file_path}")

# --- EXÉCUTION PRINCIPALE ---

if __name__ == "__main__":
    print("Démarrage du script de traitement de profil...")

    # 1. Lecture des fichiers
    source_data = read_json_file(SOURCE_FILE_PATH)
    template_data = read_json_file(TEMPLATE_FILE_PATH)
    mapping_config = read_json_file(MAPPING_CONFIG_FILE)

    if source_data and template_data and mapping_config:
        # 2. Transformation des données
        transformed_data = transform_data(source_data, template_data, mapping_config)

        # 3. Enrichissement avec Gemini
        enriched_data = enrich_with_gemini(transformed_data)

        # 4. Écriture du fichier final
        write_json_file(enriched_data, OUTPUT_FILE_PATH)

    print("Script terminé.")
