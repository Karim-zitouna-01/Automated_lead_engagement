import json
from pathlib import Path
from typing import Dict, Any, List
import uuid

class FileManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.icp_path = self.data_dir / "icp.json"
        self.leads_dir = self.data_dir / "leads"
        
        self._init_directories()
    
    def _init_directories(self):
        self.leads_dir.mkdir(parents=True, exist_ok=True)
        if not self.icp_path.exists():
            self._create_default_icp()
    
    def _create_default_icp(self):
        default_icp = {
            "service": "Default Service",
            "ideal_customer_profile": {
                "industry": [],
                "company_size": {},
                "geography": [],
                "technology_maturity": "",
                "existing_stack": []
            }
        }
        self.save_icp(default_icp)
    
    def load_icp(self) -> Dict[str, Any]:
        with open(self.icp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_icp(self, icp_data: Dict[str, Any]):
        with open(self.icp_path, 'w', encoding='utf-8') as f:
            json.dump(icp_data, f, indent=2)
    
    def save_lead_report(self, filename: str, content: str):
        report_path = self.leads_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        leads = []
        for file in self.leads_dir.glob("*.txt"):
            with open(file, 'r', encoding='utf-8') as f:
                leads.append({
                    "filename": file.name,
                    "content": f.read()
                })
        return leads
    
    def get_lead_file(self, filename: str) -> str:
        filepath = self.leads_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Lead file {filename} not found")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()