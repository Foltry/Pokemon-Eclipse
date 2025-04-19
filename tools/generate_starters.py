# tools/generate_starters.py

import os
import json
import requests
from logger import log_error

OUTPUT_PATH = os.path.join("data", "starters.json")
POKEAPI_BASE = "https://pokeapi.co/api/v2"

# IDs Pokédex national des 15 starters (1 à 5G)
STARTER_IDS = [
    1, 4, 7,        # Gen 1 : Bulbasaur, Charmander, Squirtle
    152, 155, 158,  # Gen 2 : Chikorita, Cyndaquil, Totodile
    252, 255, 258,  # Gen 3 : Treecko, Torchic, Mudkip
    387, 390, 393,  # Gen 4 : Turtwig, Chimchar, Piplup
    495, 498, 501   # Gen 5 : Snivy, Tepig, Oshawott
]


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_starters.py", f"Erreur lors du fetch {url} : {e}")
        return None


def extract_starter_data(pokemon_id):
    pokemon_data = fetch_json(f"{POKEAPI_BASE}/pokemon/{pokemon_id}")
    species_data = fetch_json(f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}")

    if not pokemon_data or not species_data:
        return None

    try:
        name_en = pokemon_data["name"]
        name_fr = next((n["name"] for n in species_data["names"] if n["language"]["name"] == "fr"), name_en)

        types = [t["type"]["name"] for t in sorted(pokemon_data["types"], key=lambda x: x["slot"])]

        stats = {s["stat"]["name"]: s["base_stat"] for s in pokemon_data["stats"]}

        return {
            "id": pokemon_id,
            "name_en": name_en,
            "name_fr": name_fr,
            "types": types,
            "base_stats": stats
        }

    except Exception as e:
        log_error("generate_starters.py", f"Erreur parsing starter #{pokemon_id} : {e}")
        return None


def main():
    starters = []

    for pid in STARTER_IDS:
        print(f"-> Récupération starter #{pid}")
        data = extract_starter_data(pid)
        if data:
            starters.append(data)
        else:
            log_error("generate_starters.py", f"Erreur récupération starter #{pid}")

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(starters, f, ensure_ascii=False, indent=2)

    print(f"OK {len(starters)} starters sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
