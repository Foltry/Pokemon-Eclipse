import os
import json
import requests
from tqdm import tqdm

POKEAPI_BASE = "https://pokeapi.co/api/v2"
DATA_DIR = "data"
MOVE_LIMIT = 1000  # Pour couvrir toutes les attaques connues

# === UTILS ===

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === FETCH MOVE ===

def fetch_move_data(move_id):
    try:
        data = requests.get(f"{POKEAPI_BASE}/move/{move_id}", timeout=10).json()

        # Nom en FR
        name_fr = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"])

        # Description FR
        desc_fr = next((e["effect"] for e in data["effect_entries"]
                        if e["language"]["name"] == "fr"), None)

        short_desc = next((e["short_effect"] for e in data["effect_entries"]
                           if e["language"]["name"] == "en"), "")

        return {
            "id": move_id,
            "name": name_fr,
            "type": data["type"]["name"],
            "power": data["power"],
            "pp": data["pp"],
            "accuracy": data["accuracy"],
            "priority": data["priority"],
            "damage_class": data["damage_class"]["name"],
            "target": data["target"]["name"],
            "description": desc_fr or short_desc,
            "effect_chance": data["effect_chance"],
            "meta": data["meta"] if data["meta"] else {},
            "generation": data["generation"]["name"]
        }

    except Exception as e:
        print(f"❌ Erreur attaque {move_id}: {e}")
        return None

# === MAIN ===

def main():
    ensure_dir(DATA_DIR)

    moves = {}

    print("⚔️ Récupération des attaques...")
    for move_id in tqdm(range(1, MOVE_LIMIT + 1)):
        move = fetch_move_data(move_id)
        if move:
            moves[move["name"].lower().replace(" ", "-")] = move

    save_json(os.path.join(DATA_DIR, "moves.json"), moves)
    print("✅ Fichier moves.json généré.")

if __name__ == "__main__":
    main()
