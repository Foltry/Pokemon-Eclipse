# tools/generate_moves.py

import os
import json
import requests
from logger import log_error

POKEAPI_BASE = "https://pokeapi.co/api/v2"
OUTPUT_PATH = os.path.join("data", "moves.json")


def fetch_json(url):
    """
    Effectue une requête HTTP GET vers une URL et retourne les données JSON.

    Args:
        url (str): URL à interroger.

    Returns:
        dict | None: Données JSON si succès, sinon None.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_moves.py", f"Erreur lors du fetch {url} : {e}")
        return None


def get_all_move_urls():
    """
    Récupère toutes les URLs des attaques connues via la PokéAPI.

    Returns:
        list[str]: Liste d'URLs d'attaques.
    """
    url = f"{POKEAPI_BASE}/move?limit=1000"
    data = fetch_json(url)
    return [m["url"] for m in data["results"]] if data else []


def extract_move_data(url):
    """
    Extrait toutes les données utiles d’une attaque à partir de son URL API.

    Args:
        url (str): URL de l’attaque dans la PokéAPI.

    Returns:
        dict | None: Données formatées ou None en cas d’erreur.
    """
    move = fetch_json(url)
    if not move:
        return None

    try:
        name_en = move["name"]
        name_fr = next((n["name"] for n in move.get("names", []) if n["language"]["name"] == "fr"), name_en)

        # Texte d'effet (court), avec substitution de $effect_chance
        effect_entry_fr = next((e for e in move.get("effect_entries", []) if e["language"]["name"] == "fr"), None)
        effect_text = (
            effect_entry_fr["short_effect"].replace("$effect_chance", str(move.get("effect_chance", "")))
            if effect_entry_fr else ""
        )

        # Texte de description (flavor text)
        flavor_fr = next(
            (f["flavor_text"].replace("\n", " ") for f in reversed(move.get("flavor_text_entries", []))
             if f["language"]["name"] == "fr" and f["version_group"]["name"] == "firered-leafgreen"),
            ""
        )
        if not flavor_fr:
            flavor_fr = next(
                (f["flavor_text"].replace("\n", " ") for f in reversed(move.get("flavor_text_entries", []))
                 if f["language"]["name"] == "fr"),
                ""
            )

        return {
            "id": move["id"],
            "name_en": name_en,
            "name_fr": name_fr,
            "type": move["type"]["name"],
            "damage_class": move.get("damage_class", {}).get("name"),
            "power": move.get("power"),
            "accuracy": move.get("accuracy"),
            "pp": move.get("pp"),
            "priority": move.get("priority"),
            "effect": effect_text,
            "description": flavor_fr,
            "effect_chance": move.get("effect_chance"),
            "ailment": move.get("meta", {}).get("ailment", {}).get("name"),
            "target": move.get("target", {}).get("name"),
        }

    except Exception as e:
        log_error("generate_moves.py", f"Erreur parsing move {url} : {e}")
        return None


def main():
    """
    Script principal. Récupère toutes les attaques, les convertit,
    puis les sauvegarde dans data/moves.json.
    """
    move_urls = get_all_move_urls()
    all_moves = []

    for i, url in enumerate(move_urls, start=1):
        print(f"-> Récupération attaque {i}/{len(move_urls)}")
        move_data = extract_move_data(url)
        if move_data:
            all_moves.append(move_data)
        else:
            log_error("generate_moves.py", f"Erreur récupération move à {url}")

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_moves, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_moves)} attaques sauvegardées dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
