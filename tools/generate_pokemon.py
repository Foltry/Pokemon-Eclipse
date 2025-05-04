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
    """
    Récupère un objet JSON via HTTP GET.

    Args:
        url (str): URL cible.

    Returns:
        dict | None: Résultat JSON ou None en cas d’erreur.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_pokemon.py", f"Erreur fetch {url} : {e}")
        return None


def get_localized_name(obj, lang="fr"):
    """
    Extrait le nom localisé d’un objet PokéAPI.

    Args:
        obj (dict): Données JSON contenant un champ "names".
        lang (str): Langue cible (fr par défaut).

    Returns:
        str: Nom localisé ou nom brut.
    """
    for entry in obj.get("names", []):
        if entry["language"]["name"] == lang:
            return entry["name"]
    return obj.get("name", "inconnu")


def get_move_name_fr(url):
    """
    Récupère le nom français d’un move depuis son URL API.

    Args:
        url (str): URL de la move.

    Returns:
        str: Nom français ou "inconnu".
    """
    if url not in move_cache:
        move_cache[url] = fetch_json(url)
    move_data = move_cache[url]
    return get_localized_name(move_data) if move_data else "inconnu"


def build_sprite_name(pokemon_id, variant):
    """
    Construit le nom de fichier du sprite pour un Pokémon donné.

    Args:
        pokemon_id (int): ID du Pokémon.
        variant (str): Variante du sprite (front, back, etc.).

    Returns:
        str: Nom de fichier.
    """
    return f"{str(pokemon_id).zfill(3)}_{variant}.gif"


def extract_sprites(pokemon_id):
    """
    Génère les chemins de sprite pour toutes les variantes connues.

    Args:
        pokemon_id (int): ID du Pokémon.

    Returns:
        dict: Dictionnaire des sprites.
    """
    variants = [
        "front", "back",
        "front_shiny", "back_shiny",
        "front_female", "back_female",
        "front_shiny_female", "back_shiny_female"
    ]
    return {variant: build_sprite_name(pokemon_id, variant) for variant in variants}


def parse_evolution_chain(chain):
    """
    Transforme une chaîne d’évolution récursive en dictionnaire.

    Args:
        chain (dict): Branche de la chaîne.

    Returns:
        dict: Arbre d’évolution.
    """
    return {
        "species": chain["species"]["name"],
        "evolves_to": [parse_evolution_chain(evo) for evo in chain["evolves_to"]]
    }


def extract_pokemon_data(pokemon_id):
    """
    Extrait toutes les données pertinentes pour un Pokémon donné.

    Args:
        pokemon_id (int): Identifiant Pokédex.

    Returns:
        dict | None: Données formatées ou None si erreur.
    """
    data = fetch_json(f"{POKEAPI_BASE}/pokemon/{pokemon_id}")
    species = fetch_json(f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}")

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

    level_up_moves = sorted(level_up_moves, key=lambda m: m["level"])

    evo_chain_data = fetch_json(species.get("evolution_chain", {}).get("url")) if species.get("evolution_chain") else None
    evolution_chain = parse_evolution_chain(evo_chain_data["chain"]) if evo_chain_data else []

    return {
        "id": pokemon_id,
        "name": name_fr,
        "base_experience": data.get("base_experience", 0),
        "types": types,
        "height": data.get("height", 0),
        "weight": data.get("weight", 0),
        "stats": stats,
        "moves": level_up_moves,
        "evolution": evolution_chain,
        "sprites": extract_sprites(pokemon_id)
    }


def main():
    """
    Point d’entrée principal du script.
    Récupère toutes les données des Pokémon dans l’intervalle POKEMON_RANGE,
    puis les écrit dans le fichier final JSON.
    """
    all_pokemon = []

    for pid in POKEMON_RANGE:
        print(f"-> Récupération Pokémon #{pid}")
        data = extract_pokemon_data(pid)
        if data:
            all_pokemon.append(data)
        else:
            log_error("generate_pokemon.py", f"Erreur récupération Pokémon #{pid}")
        time.sleep(0.3)  # Pour ne pas surcharger l'API

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_pokemon, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_pokemon)} Pokémon sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
