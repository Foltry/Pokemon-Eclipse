import os
import json
import requests
from tqdm import tqdm

POKEAPI_BASE = "https://pokeapi.co/api/v2"
DATA_DIR = "data"
SPRITE_DIR = "assets/sprites/items"
CATEGORIES = [
    "standard-balls", "healing", "status-cures", "vitamins",
    "pp-recovery", "revival", "stat-boosts", "medicine"
]

# === UTILS ===

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def download_sprite(sprite_url, local_path):
    if not os.path.exists(local_path):
        try:
            r = requests.get(sprite_url, timeout=10)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass

# === ITEM DATA ===

def fetch_item(item_url):
    try:
        data = requests.get(item_url, timeout=10).json()
        name_fr = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"])
        effect_fr = next((e["short_effect"] for e in data["effect_entries"]
                          if e["language"]["name"] == "fr"), None)

        sprite_url = data["sprites"]["default"]
        item_id = int(data["id"])
        sprite_path = os.path.join(SPRITE_DIR, f"{item_id}.png")
        if sprite_url:
            download_sprite(sprite_url, sprite_path)

        return item_id, {
            "id": item_id,
            "name": name_fr,
            "category": data["category"]["name"],
            "cost": data["cost"],
            "effect": effect_fr,
            "sprite": f"{item_id}.png" if sprite_url else None
        }

    except Exception as e:
        print(f"❌ Erreur item {item_url} : {e}")
        return None, None

# === MAIN ===

def main():
    ensure_dir(DATA_DIR)
    ensure_dir(SPRITE_DIR)

    all_items = {}

    print("🎒 Récupération des objets...")
    for category in CATEGORIES:
        try:
            cat_data = requests.get(f"{POKEAPI_BASE}/item-category/{category}", timeout=10).json()
            items = cat_data["items"]

            for item in tqdm(items, desc=f"📦 {category}"):
                item_id, item_data = fetch_item(item["url"])
                if item_id and item_data:
                    all_items[str(item_id)] = item_data

        except Exception as e:
            print(f"❌ Erreur catégorie {category}: {e}")

    save_json(os.path.join(DATA_DIR, "items.json"), all_items)
    print(f"✅ Fichier items.json généré avec {len(all_items)} objets.")

if __name__ == "__main__":
    main()
