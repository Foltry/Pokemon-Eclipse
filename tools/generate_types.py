import os
import json
import requests
from tqdm import tqdm

POKEAPI_BASE = "https://pokeapi.co/api/v2"
DATA_DIR = "data"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_type_data(type_id):
    try:
        url = f"{POKEAPI_BASE}/type/{type_id}"
        data = requests.get(url, timeout=10).json()

        name_en = data["name"]
        name_fr = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), name_en)

        damage_relations = data["damage_relations"]
        relations = {
            "double_damage_from": [t["name"] for t in damage_relations["double_damage_from"]],
            "double_damage_to": [t["name"] for t in damage_relations["double_damage_to"]],
            "half_damage_from": [t["name"] for t in damage_relations["half_damage_from"]],
            "half_damage_to": [t["name"] for t in damage_relations["half_damage_to"]],
            "no_damage_from": [t["name"] for t in damage_relations["no_damage_from"]],
            "no_damage_to": [t["name"] for t in damage_relations["no_damage_to"]],
        }

        return {
            "id": type_id,
            "name": name_fr,
            "relations": relations
        }

    except Exception as e:
        print(f"❌ Erreur type {type_id} : {e}")
        return None

def main():
    ensure_dir(DATA_DIR)
    types = {}

    print("🧪 Récupération des types...")
    for i in tqdm(range(1, 19), desc="Types"):
        type_data = fetch_type_data(i)
        if type_data:
            types[str(i)] = type_data

    save_json(os.path.join(DATA_DIR, "types.json"), types)
    print(f"✅ Fichier types.json généré avec {len(types)} types.")

if __name__ == "__main__":
    main()
