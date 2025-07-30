import requests
import json
import os

def update_leads_data(service_name: str, output_file: str = "leads_data.json", api_url: str = "http://localhost:8002/api/find_leads"):
    """
    Récupère les données de l'API /api/find_leads et les stocke dans un fichier JSON.

    Args:
        service_name (str): Le nom du service pour lequel trouver les leads.
        output_file (str): Le nom du fichier JSON de sortie.
        api_url (str): L'URL de l'endpoint /api/find_leads.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"service_name": service_name}

    print(f"Appel de l'API {api_url} pour le service: {service_name}...")
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP d'erreur (4xx ou 5xx)

        leads_data = response.json()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, ensure_ascii=False, indent=2)

        print(f"Données des leads sauvegardées avec succès dans '{output_file}'.")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel de l'API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse de l'API: {e.response.text}")
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON de la réponse de l'API.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")

if __name__ == "__main__":
    # Exemple d'utilisation :
    # Assurez-vous que votre serveur FastAPI est en cours d'exécution sur http://localhost:8002
    # et que le service 'Data & AI Consulting' est configuré dans votre icp.json.
    
    # Remplacez 'Data & AI Consulting' par le nom du service que vous souhaitez tester.
    service_to_update = "Data & AI Consulting" 
    update_leads_data(service_to_update)
