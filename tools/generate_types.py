import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
LOG_PATH = os.path.join("tools", "logs")
os.makedirs(LOG_PATH, exist_ok=True)
ERROR_LOG_FILE = os.path.join(LOG_PATH, "generation_errors.log")

def log_error(script_name, error_text):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"--- Erreur dans {script_name} ---\n")
        log_file.write(error_text + "\n\n")

if __name__ == "__main__":
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        import os
        import json
        import requests
        from tqdm import tqdm
        from core.data_loader import load_json, save_json, ensure_dir
        
        DATA_PATH = "data/types.json"
        
        def fetch_type(type_id):
            url = f"https://pokeapi.co/api/v2/type/{type_id}/"
            try:
                res = requests.get(url)
                if res.status_code != 200:
                    return None
                return res.json()
            except Exception:
                return None
        
        def extract_data(raw):
            name = next((n['name'] for n in raw['names'] if n['language']['name'] == 'fr'), raw['name'])
            relations = raw["damage_relations"]
            return {
                "name": name,
                "double_damage_from": [t['name'] for t in relations['double_damage_from']],
                "double_damage_to": [t['name'] for t in relations['double_damage_to']],
                "half_damage_from": [t['name'] for t in relations['half_damage_from']],
                "half_damage_to": [t['name'] for t in relations['half_damage_to']],
                "no_damage_from": [t['name'] for t in relations['no_damage_from']],
                "no_damage_to": [t['name'] for t in relations['no_damage_to']],
            }
        
        def main():
            ensure_dir("data/")
            try:
                data = load_json(DATA_PATH) if os.path.exists(DATA_PATH) else {}
        
                for i in tqdm(range(1, 19), desc="🧪 Récupération des types"):
                    if str(i) in data:
                        continue
                    raw = fetch_type(i)
                    if not raw:
                        continue
        
                    info = extract_data(raw)
                    data[str(i)] = info
                    print(f"✅ Type ajouté : {info['name']} ({i})")
        
                save_json(DATA_PATH, data)
                print("✅ Données types sauvegardées.")
            except KeyboardInterrupt:
                print("⏹ Interruption demandée, sauvegarde partielle...")
                save_json(DATA_PATH, data)
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_types.py: {e}")
        log_error("generate_types.py", error_details)
