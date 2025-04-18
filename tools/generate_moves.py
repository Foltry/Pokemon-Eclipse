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
        
        DATA_PATH = "data/moves.json"
        
        def fetch_move(move_id):
            url = f"https://pokeapi.co/api/v2/move/{move_id}/"
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    return None
                return response.json()
            except Exception:
                return None
        
        def extract_data(raw):
            name = next((n['name'] for n in raw['names'] if n['language']['name'] == 'fr'), raw['name'])
            desc = next((d['flavor_text'] for d in raw['flavor_text_entries'] if d['language']['name'] == 'fr'), "")
            return {
                "name": name,
                "type": raw['type']['name'],
                "category": raw['damage_class']['name'],
                "power": raw['power'],
                "accuracy": raw['accuracy'],
                "pp": raw['pp'],
                "priority": raw['priority'],
                "effect": desc.strip()
            }
        
        def main():
            ensure_dir("data/")
            try:
                data = load_json(DATA_PATH) if os.path.exists(DATA_PATH) else {}
        
                for i in tqdm(range(1, 1000), desc="⚔️ Récupération des attaques"):
                    if str(i) in data:
                        continue
                    raw = fetch_move(i)
                    if not raw:
                        continue
        
                    info = extract_data(raw)
                    data[str(i)] = info
                    print(f"✅ Attaque ajoutée : {info['name']} ({raw['name']})")
        
                save_json(DATA_PATH, data)
                print("✅ Données attaques sauvegardées.")
            except KeyboardInterrupt:
                print("⏹ Interruption demandée, sauvegarde partielle...")
                save_json(DATA_PATH, data)
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_moves.py: {e}")
        log_error("generate_moves.py", error_details)
