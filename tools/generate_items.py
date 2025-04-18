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
        from core.data_loader import load_json, ensure_dir, file_exists, save_json
        
        
        DATA_PATH = "data/items.json"
        SPRITE_DIR = "assets/sprites/items/"
        CATEGORIES = ["standard-balls", "healing", "status-cures", "medicine"]
        
        def fetch_item_data(item_id):
            url = f"https://pokeapi.co/api/v2/item/{item_id}/"
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    return None
                return response.json()
            except Exception:
                return None
        
        def extract_data(raw):
            name = next((n['name'] for n in raw['names'] if n['language']['name'] == 'fr'), raw['name'])
            desc = next((d['text'] for d in raw['flavor_text_entries'] if d['language']['name'] == 'fr'), "")
            return {
                "name": name,
                "category": raw['category']['name'],
                "cost": raw['cost'],
                "effect": desc.replace("\n", " ").replace("\f", " ").strip()
            }
        
        def main():
            ensure_dir(SPRITE_DIR)
            try:
                data = load_json(DATA_PATH) if os.path.exists(DATA_PATH) else {}
        
                for i in tqdm(range(1, 1000), desc="🔽 Téléchargement objets"):
                    if str(i) in data:
                        continue
                    raw = fetch_item_data(i)
                    if not raw or raw["category"]["name"] not in CATEGORIES:
                        continue
        
                    info = extract_data(raw)
                    data[str(i)] = info
                    print(f"✅ Objet ajouté : {info['name']} ({i})")
        
                    # Sprite
                    sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/{raw['name']}.png"
                    sprite_path = os.path.join(SPRITE_DIR, f"{i}.png")
                    if not os.path.exists(sprite_path):
                        try:
                            sprite = requests.get(sprite_url)
                            if sprite.status_code == 200:
                                with open(sprite_path, "wb") as f:
                                    f.write(sprite.content)
                                print(f"⬇️ Sprite objet : {i}")
                        except Exception:
                            pass
        
                save_json(DATA_PATH, data)
                print("✅ Données objets sauvegardées.")
            except KeyboardInterrupt:
                print("⏹ Interruption demandée, sauvegarde partielle...")
                save_json(DATA_PATH, data)
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_items.py: {e}")
        log_error("generate_items.py", error_details)
