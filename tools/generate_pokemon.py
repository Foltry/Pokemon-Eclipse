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
        import os
        import sys
        import json
        import requests
        from tqdm import tqdm
        
        # Corriger les imports relatifs au projet
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from core.data_loader import load_json, save_json, ensure_dir, file_exists
        
        POKEMON_URL = "https://pokeapi.co/api/v2/pokemon/"
        OUTPUT_PATH = "data/pokemon.json"
        MAX_POKEMON_ID = 649  # Générations 1 à 5
        
        def fetch_pokemon_data(poke_id: int) -> dict:
            url = f"{POKEMON_URL}{poke_id}"
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"Erreur lors de la requête pour l'ID {poke_id}")
            return response.json()
        
        def fetch_species_data(url: str) -> dict:
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"Erreur lors de la requête species : {url}")
            return response.json()
        
        def extract_data(poke_id: int, raw: dict) -> dict:
            species_data = fetch_species_data(raw["species"]["url"])
            name = next((n["name"] for n in species_data["names"] if n["language"]["name"] == "fr"), raw["name"])
        
            types = [t["type"]["name"] for t in raw["types"]]
            stats = {s["stat"]["name"]: s["base_stat"] for s in raw["stats"]}
            sprite_url = raw["sprites"]["front_default"]
        
            return {
                "name": name,
                "types": types,
                "base_hp": stats.get("hp", 0),
                "base_attack": stats.get("attack", 0),
                "base_defense": stats.get("defense", 0),
                "base_speed": stats.get("speed", 0),
                "base_experience": raw.get("base_experience", 0),
                "sprite_url": sprite_url
            }
        
        def main():
            ensure_dir("data")
            data = load_json(OUTPUT_PATH) if file_exists(OUTPUT_PATH) else {}
        
            for i in tqdm(range(1, MAX_POKEMON_ID + 1), desc="🔄 Récupération des Pokémon"):
                str_id = str(i).zfill(3)
                if str_id in data:
                    continue
        
                try:
                    raw = fetch_pokemon_data(i)
                    info = extract_data(i, raw)
                    data[str_id] = info
                except Exception as e:
                    print(f"❌ Erreur Pokémon {i}: {e}")
        
            save_json(OUTPUT_PATH, data)
            print("✅ Données Pokémon sauvegardées.")
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_pokemon.py: {e}")
        log_error("generate_pokemon.py", error_details)
