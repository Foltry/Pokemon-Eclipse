import os
import json
import requests
from logger import log_error

POKEAPI_BASE = "https://pokeapi.co/api/v2"
OUTPUT_PATH = os.path.join("data", "types.json")

# Types valides jusqu’à Gen 5
VALID_TYPE_NAMES = {
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel"
}

# Traduction des classes de dégâts (move_damage_class)
COLOR_TRANSLATIONS = {
    "physical": "physique",
    "special": "spécial",
    "status": "statut"
}


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_types.py", f"Erreur lors du fetch {url} : {e}")
        return None


def get_all_type_urls():
    url = f"{POKEAPI_BASE}/type?limit=100"
    data = fetch_json(url)
    return [t["url"] for t in data["results"]] if data else []


def get_localized_name(obj, language="fr"):
    for name_entry in obj.get("names", []):
        if name_entry["language"]["name"] == language:
            return name_entry["name"]
    return obj.get("name", "inconnu")


def filter_and_translate_relations(relations):
    return [get_localized_name(t) for t in relations if t["name"] in VALID_TYPE_NAMES]


def extract_type_data(url):
    type_data = fetch_json(url)
    if not type_data:
        return None

    try:
        name_en = type_data["name"]
        if name_en not in VALID_TYPE_NAMES:
            return None

        name_fr = get_localized_name(type_data)
        generation_data = fetch_json(type_data["generation"]["url"])
        generation_fr = get_localized_name(generation_data)

        relations = type_data["damage_relations"]
        damage_relations = {
            "double_damage_from": filter_and_translate_relations(relations["double_damage_from"]),
            "double_damage_to": filter_and_translate_relations(relations["double_damage_to"]),
            "half_damage_from": filter_and_translate_relations(relations["half_damage_from"]),
            "half_damage_to": filter_and_translate_relations(relations["half_damage_to"]),
            "no_damage_from": filter_and_translate_relations(relations["no_damage_from"]),
            "no_damage_to": filter_and_translate_relations(relations["no_damage_to"]),
        }

        raw_color = type_data.get("move_damage_class", {}).get("name")
        color_fr = COLOR_TRANSLATIONS.get(raw_color, "inconnu")

        return {
            "id": type_data["id"],
            "name": name_fr,
            "generation": generation_fr,
            "color": color_fr,
            "damage_relations": damage_relations
        }

    except Exception as e:
        log_error("generate_types.py", f"Erreur parsing type {url} : {e}")
        return None


def main():
    type_urls = get_all_type_urls()
    all_types = []

    for i, url in enumerate(type_urls, start=1):
        print(f"-> Récupération type {i}/{len(type_urls)}")
        type_data = extract_type_data(url)
        if type_data:
            all_types.append(type_data)

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_types, f, ensure_ascii=False, indent=2)

    print(f"OK {len(all_types)} types sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
