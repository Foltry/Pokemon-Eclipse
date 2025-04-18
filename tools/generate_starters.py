import os
import json
import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"
DATA_DIR = "data"
GEN_LIMIT = 5

# Liste des noms des starters de chaque génération (premiers stades uniquement)
STARTER_NAMES = [
    # Gen 1
    "bulbasaur", "charmander", "squirtle",
    # Gen 2
    "chikorita", "cyndaquil", "totodile",
    # Gen 3
    "treecko", "torchic", "mudkip",
    # Gen 4
    "turtwig", "chimchar", "piplup",
    # Gen 5
    "snivy", "tepig", "oshawott"
]

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_pokemon_id(name):
    try:
        url = f"{POKEAPI_BASE}/pokemon/{name.lower()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return str(response.json()["id"])
    except Exception as e:
        print(f"❌ Erreur starter {name} : {e}")
        return None

def main():
    ensure_dir(DATA_DIR)
    ids = []

    for name in STARTER_NAMES:
        poke_id = get_pokemon_id(name)
        if poke_id:
            ids.append(poke_id)

    if len(ids) < 3:
        print("❌ Moins de 3 starters trouvés, échec.")
    else:
        path = os.path.join(DATA_DIR, "starters.json")
        save_json(path, ids)
        print(f"✅ Fichier starters.json généré avec {len(ids)} starters.")

if __name__ == "__main__":
    main()
