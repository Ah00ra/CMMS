# http_service.py
import requests


class HttpDBService:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_equip_detail(self, equip_code):
        r = requests.get(f"{self.base_url}/equipment/{equip_code}")
        r.raise_for_status()
        return r.json()

    def load_equipment_table(self):
        r = requests.get(f"{self.base_url}/equipment")
        r.raise_for_status()
        
        # Convert dicts back to tuples for MainWindow compatibility
        data = r.json()
        return [(item["equipment_code"], item["location"], item["pm_type"]) for item in data]


    def mark_a_pm_done(self, equipment_code, pm_name, last_done_date):
        payload = {"pm_name": pm_name, "last_done_date": last_done_date}
        r = requests.post(f"{self.base_url}/equipment/{equipment_code}/pm_done", json=payload)
        r.raise_for_status()
        return r.json()["equipment_pm_id"]

    
    def delete_equipment(self, equip_code):
        r = requests.delete(f"{self.base_url}/equipment/{equip_code}")
        r.raise_for_status()
