# tools/generate_pokemon.py

import os
import json
import time
import requests
from logger import log_error

POKEAPI_BASE = "https://pokeapi.co/api/v2"
OUTPUT_PATH = os.path.join("data", "pokemon.json")
VERSION_GROUP = "firered-leafgreen"
POKEMON_RANGE = range(1, 650)

move_cache = {}

def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_pokemon.py", f"Erreur fetch {url} : {e}")
        return None

def get_localized_name(obj, lang="fr"):
    for entry in obj.get("names", []):
        if entry["language"]["name"] == lang:
            return entry["name"]
    return obj["name"]

def get_move_name_fr(url):
    if url not in move_cache:
        move_cache[url] = fetch_json(url)
    move_data = move_cache[url]
    return get_localized_name(move_data) if move_data else "inconnu"

def build_sprite_name(pokemon_id, variant):
    return f"{str(pokemon_id).zfill(3)}_{variant}.gif"

def extract_sprites(pokemon_id):
    variants = [
        "front", "back",
        "front_shiny", "back_shiny",
        "front_female", "back_female",
        "front_shiny_female", "back_shiny_female"
    ]
    sprite_dict = {variant: build_sprite_name(pokemon_id, variant) for variant in variants}
    return sprite_dict

def parse_evolution_chain(chain):
    return {
        "species": chain["species"]["name"],
        "evolves_to": [parse_evolution_chain(evo) for evo in chain["evolves_to"]]
    }

def extract_pokemon_data(pokemon_id):
    url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
    species_url = f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}"

    data = fetch_json(url)
    species = fetch_json(species_url)

    if not data or not species:
        return None

    name_fr = get_localized_name(species)
    types = [get_localized_name(t["type"]) for t in sorted(data["types"], key=lambda x: x["slot"])]
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    level_up_moves = []
    for move in data["moves"]:
        for v in move["version_group_details"]:
            if v["version_group"]["name"] == VERSION_GROUP and v["move_learn_method"]["name"] == "level-up":
                move_name_fr = get_move_name_fr(move["move"]["url"])
                level_up_moves.append({
                    "name": move_name_fr,
                    "level": v["level_learned_at"]
                })
    level_up_moves.sort(key=lambda m: m["level"])

    evo_chain_data = fetch_json(species["evolution_chain"]["url"]) if species.get("evolution_chain") else None
    evolution_chain = parse_evolution_chain(evo_chain_data["chain"]) if evo_chain_data else []

    sprites = extract_sprites(pokemon_id)

    return {
        "id": pokemon_id,
        "name": name_fr,
        "base_experience": data.get("base_experience", 0),
        "types": types,
        "height": data["height"],
        "weight": data["weight"],
        "stats": stats,
        "moves": level_up_moves,
        "evolution": evolution_chain,
        "sprites": sprites
    }

def main():
    all_pokemon = []

    for pid in POKEMON_RANGE:
        print(f"-> Récupération Pokémon #{pid}")
        data = extract_pokemon_data(pid)
        if data:
            all_pokemon.append(data)
        else:
            log_error("generate_pokemon.py", f"Erreur récupération Pokémon #{pid}")
        time.sleep(0.3)  # Limite API

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_pokemon, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_pokemon)} Pokémon sauvegardés dans {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
