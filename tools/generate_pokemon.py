import os
import json
import requests
from tqdm import tqdm

POKEAPI_BASE = "https://pokeapi.co/api/v2"
POKEMON_COUNT = 649  # GEN 1 à 5

DATA_DIR = "data"
SPRITE_DIR = os.path.join("assets", "sprites", "pokemon", "front")

# === UTILS ===

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === SPRITES ===

def download_sprite(pokemon_id, url):
    if not url:
        return
    filename = os.path.join(SPRITE_DIR, f"{str(pokemon_id).zfill(3)}.png")
    if os.path.exists(filename):
        return
    try:
        img = requests.get(url, timeout=10).content
        with open(filename, "wb") as f:
            f.write(img)
    except Exception as e:
        print(f"❌ Sprite {pokemon_id}: {e}")

# === FETCH POKEMON ===

def fetch_pokemon_data(pokemon_id):
    try:
        poke_data = requests.get(f"{POKEAPI_BASE}/pokemon/{pokemon_id}", timeout=10).json()
        species_data = requests.get(f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}", timeout=10).json()

        # Types, stats
        types = [t["type"]["name"] for t in poke_data["types"]]
        stats = {s["stat"]["name"]: s["base_stat"] for s in poke_data["stats"]}
        abilities = [a["ability"]["name"] for a in poke_data["abilities"]]
        held_items = [item["item"]["name"] for item in poke_data["held_items"]]

        # Moves
        moves = [{
            "name": m["move"]["name"],
            "level": d["level_learned_at"]
        } for m in poke_data["moves"] for d in m["version_group_details"]
            if d["move_learn_method"]["name"] == "level-up" and d["level_learned_at"] > 0]

        moves = sorted(moves, key=lambda x: x["level"])

        # Description FR
        desc = next((entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                     for entry in species_data["flavor_text_entries"]
                     if entry["language"]["name"] == "fr"), "")

        # Sprite (PNG)
        sprite_url = poke_data["sprites"]["front_default"]
        download_sprite(pokemon_id, sprite_url)

        return {
            "id": pokemon_id,
            "name": poke_data["name"],
            "types": types,
            "stats": stats,
            "base_experience": poke_data["base_experience"],
            "height": poke_data["height"],
            "weight": poke_data["weight"],
            "abilities": abilities,
            "held_items": held_items,
            "moves": moves,
            "description": desc,
            "capture_rate": species_data["capture_rate"],
            "is_baby": species_data["is_baby"],
            "is_legendary": species_data["is_legendary"],
            "is_mythical": species_data["is_mythical"],
            "habitat": species_data["habitat"]["name"] if species_data["habitat"] else None,
            "generation": species_data["generation"]["name"]
        }

    except Exception as e:
        print(f"❌ Erreur Pokémon {pokemon_id} : {e}")
        return None

# === MAIN ===

def main():
    ensure_dir(DATA_DIR)
    ensure_dir(SPRITE_DIR)

    all_pokemon = {}

    print("🔄 Téléchargement des Pokémon (GEN 1 à 5)...")
    for pid in tqdm(range(1, POKEMON_COUNT + 1)):
        data = fetch_pokemon_data(pid)
        if data:
            all_pokemon[str(pid).zfill(3)] = data

    save_json(os.path.join(DATA_DIR, "pokemon.json"), all_pokemon)
    print("✅ Fichier pokemon.json généré.")

if __name__ == "__main__":
    main()
