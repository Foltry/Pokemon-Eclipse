import os
import json
import requests
from logger import log_error

POKEAPI_BASE = "https://pokeapi.co/api/v2"
OUTPUT_PATH = os.path.join("data", "items.json")
SPRITE_DIR = os.path.join("assets", "sprites", "items")

ALLOWED_CATEGORIES = {
    "standard-balls",
    "healing",
    "status-cures",
    "medicine"
}


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error("generate_items.py", f"Erreur lors du fetch {url} : {e}")
        return None


def download_sprite(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs(SPRITE_DIR, exist_ok=True)
        path = os.path.join(SPRITE_DIR, filename)
        with open(path, "wb") as f:
            f.write(response.content)
        return filename
    except Exception as e:
        log_error("generate_items.py", f"Erreur téléchargement sprite {filename} : {e}")
        return None


def get_localized_name(obj, lang="fr"):
    for entry in obj.get("names", []):
        if entry["language"]["name"] == lang:
            return entry["name"]
    return obj["name"]


def get_item_effect(item):
    # 1. Effet court FR (s'il existe)
    for entry in item.get("effect_entries", []):
        if entry["language"]["name"] == "fr":
            return entry.get("short_effect") or entry.get("effect") or ""

    # 2. Sinon, texte long via flavor_text_entries
    recent_versions = {"sword-shield", "ultra-sun-ultra-moon", "x-y", "black-white"}
    flavor_texts = [
        entry["text"] for entry in item.get("flavor_text_entries", [])
        if entry["language"]["name"] == "fr" and entry["version_group"]["name"] in recent_versions
    ]
    if flavor_texts:
        return flavor_texts[0].replace("\n", " ").strip()

    # 3. Fallback EN si vraiment rien
    for entry in item.get("effect_entries", []):
        if entry["language"]["name"] == "en":
            return entry.get("short_effect") or entry.get("effect") or ""

    return ""


def extract_item_data(url):
    item = fetch_json(url)
    if not item:
        return None

    try:
        category_id = item["category"]["name"]
        if category_id not in ALLOWED_CATEGORIES:
            return None

        name = get_localized_name(item)
        effect = get_item_effect(item)

        # Traduction de la catégorie
        category_data = fetch_json(item["category"]["url"])
        category = get_localized_name(category_data)

        sprite_url = item["sprites"]["default"]
        sprite_filename = f"{item['name']}.png"
        sprite_path = os.path.join(SPRITE_DIR, sprite_filename)
        sprite = None

        if sprite_url:
            if not os.path.exists(sprite_path):
                sprite = download_sprite(sprite_url, sprite_filename)
            else:
                sprite = sprite_filename

        return {
            "id": item["id"],
            "name": name,
            "category": category,
            "cost": item["cost"],
            "effect": effect,
            "sprite": sprite
        }

    except Exception as e:
        log_error("generate_items.py", f"Erreur parsing item {url} : {e}")
        return None


def get_all_item_urls():
    url = f"{POKEAPI_BASE}/item?limit=1000"
    data = fetch_json(url)
    return [i["url"] for i in data["results"]] if data else []


def main():
    item_urls = get_all_item_urls()
    all_items = []

    for i, url in enumerate(item_urls, start=1):
        print(f"-> Récupération objet {i}/{len(item_urls)}")
        item_data = extract_item_data(url)
        if item_data:
            all_items.append(item_data)

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_items)} objets sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
