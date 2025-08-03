# README - Module d'Enrichissement de Leads

Le fichier `lead_enrichment_module.py` a été créé.

## Pour l'utiliser :

Le développeur pourra importer et appeler la fonction `get_enriched_leads_report` depuis son propre code.

```python
from lead_enrichment_module import get_enriched_leads_report
import json

# Remplacez par le nom du service souhaité
service_name = "Data & AI Consulting"

# Appelez la fonction pour obtenir le rapport enrichi
report = get_enriched_leads_report(service_name)

if report:
    print("Rapport de leads enrichi :")
    print(json.dumps(report, indent=2))
else:
    print("Échec de la récupération du rapport de leads.")
```
