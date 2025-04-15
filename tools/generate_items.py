import os, json, requests
from tqdm import tqdm

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(BASE, "data")
SPRITES = os.path.join(BASE, "assets", "sprites", "items")
os.makedirs(DATA, exist_ok=True)
os.makedirs(SPRITES, exist_ok=True)

def get_french_name(data):
    return next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"])

def get_french_effect(data):
    # Priorité : effect_entries (plus technique), sinon flavor_text_entries (description longue)
    effect = next((e["short_effect"] for e in data.get("effect_entries", []) if e["language"]["name"] == "fr"), None)
    if not effect:
        effect = next((e["text"] for e in data.get("flavor_text_entries", []) if e["language"]["name"] == "fr"), "")
    return effect.strip()

def generate_items_data():
    categories = ["standard-balls", "status-cures", "healing", "medecine"]
    items = {}

    for cat in tqdm(categories, desc="📥 Items"):
        res = requests.get(f"https://pokeapi.co/api/v2/item-category/{cat}")
        if res.status_code != 200:
            print(f"⚠️ Erreur catégorie {cat}")
            continue

        try:
            cat_data = res.json()
        except:
            continue

        for item_entry in cat_data.get("items", []):
            r = requests.get(item_entry["url"])
            if r.status_code != 200:
                continue

            try:
                data = r.json()
            except:
                continue

            # Récupération FR
            name = get_french_name(data)
            effect = get_french_effect(data)

            items[name] = {
                "category": cat,
                "cost": data["cost"],
                "effect": effect
            }

            # Sprite
            sprite_url = data["sprites"]["default"]
            if sprite_url:
                filename = f"{name}.png"
                path = os.path.join(SPRITES, filename)
                if not os.path.exists(path):
                    try:
                        img = requests.get(sprite_url)
                        if img.status_code == 200:
                            with open(path, "wb") as f:
                                f.write(img.content)
                    except:
                        continue

    # Écriture finale
    with open(os.path.join(DATA, "items.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print("✅ items.json généré avec noms et effets en français.")

