import os
import json
from typing import Dict, Any, Optional

# Assurez-vous que le chemin vers core est correct si ce module est déplacé
# Si ce fichier est dans le même répertoire que 'core', cela fonctionnera.
# Sinon, vous devrez ajuster le PYTHONPATH ou le chemin d'importation.
from core.graph_pipeline import create_lead_generation_graph, LeadGenerationState

def get_enriched_leads_report(service_name: str, icp_file_path: str = "core/icp.json") -> Optional[Dict[str, Any]]:
    """
    Récupère un rapport de leads enrichi pour un service donné.

    Args:
        service_name (str): Le nom du service pour lequel générer le rapport de leads.
        icp_file_path (str): Le chemin relatif ou absolu vers le fichier icp.json.

    Returns:
        Optional[Dict[str, Any]]: Le rapport de leads enrichi sous forme de dictionnaire JSON,
                                  ou None si une erreur survient ou si le service n'est pas trouvé.
    """
    # Construire le chemin absolu pour icp.json
    # Cela suppose que icp.json est relatif au répertoire où ce script est exécuté
    # ou que le chemin fourni est déjà absolu.
    if not os.path.isabs(icp_file_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icp_full_path = os.path.join(current_dir, icp_file_path)
    else:
        icp_full_path = icp_file_path

    try:
        with open(icp_full_path, "r", encoding="utf-8") as f:
            all_services = json.load(f)['services']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erreur: Impossible de charger ou d'analyser icp.json depuis {icp_full_path}: {e}")
        return None

    selected_icp = next((s['ideal_customer_profile'] for s in all_services if s['service'] == service_name), None)
    
    if not selected_icp:
        print(f"Erreur: Service '{service_name}' non trouvé dans icp.json")
        return None

    try:
        graph = create_lead_generation_graph()
        initial_state = {
            "service_name": service_name,
            "icp": selected_icp,
            "potential_leads": []
        }
        
        final_state = graph.invoke(initial_state)
        
        report = final_state.get("report")
        if report:
            print(f"Rapport de leads généré avec succès pour le service '{service_name}'.")
            return report
        else:
            print(f"Erreur: Le rapport n'a pas pu être généré pour le service '{service_name}'.")
            return None
    except Exception as e:
        import traceback
        print(f"Une erreur inattendue est survenue lors de la génération du rapport: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Exemple d'utilisation de la fonction
    # Assurez-vous que votre serveur FastAPI n'est PAS en cours d'exécution si vous testez ici,
    # car LangGraph va lancer ses propres LLM et Tavily.
    
    service_to_test = "Data & AI Consulting" # Remplacez par un service valide de votre icp.json
    
    print(f"Génération du rapport pour le service: {service_to_test}...")
    enriched_report = get_enriched_leads_report(service_to_test)
    
    if enriched_report:
        print("\n--- RAPPORT ENRICHI ---")
        print(json.dumps(enriched_report, indent=2))
    else:
        print("\n--- ÉCHEC DE LA GÉNÉRATION DU RAPPORT ---")
