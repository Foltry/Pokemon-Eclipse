import os, json, requests, signal, sys

ITEMS_PATH = "data/items.json"
SPRITES_DIR = "assets/sprites/items"
should_exit = False

def handle_sig(sig, frame): sys.exit(0)
if hasattr(signal, "SIGTSTP"):
    signal.signal(signal.SIGTSTP, handle_sig)

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f: return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def download_sprite(name, url):
    path = os.path.join(SPRITES_DIR, name + ".png")
    if os.path.exists(path): return
    r = requests.get(url)
    if r.status_code == 200:
        with open(path, "wb") as f: f.write(r.content)

def main():
    os.makedirs(SPRITES_DIR, exist_ok=True)
    existing = load_json(ITEMS_PATH)
    all_items = {}

    url = "https://pokeapi.co/api/v2/item?limit=2000"
    r = requests.get(url)
    if r.status_code != 200: return

    for entry in r.json()["results"]:
        data = requests.get(entry["url"]).json()
        item_id = str(data["id"])
        if item_id in existing: continue

        name = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"])
        sprite_url = data["sprites"]["default"]
        if not os.path.exists(os.path.join(SPRITES_DIR, item_id + ".png")):
            print(f"⬇️ Téléchargement sprite objet : {name}")
        download_sprite(item_id, sprite_url)

        print(f"✅ Objet ajouté : {name}")
        all_items[item_id] = {
            "name": name,
            "category": data["category"]["name"],
            "cost": data["cost"]
        }

    existing.update(all_items)
    save_json(ITEMS_PATH, existing)
    print(f"✅ {len(all_items)} nouveaux objets ajoutés.")

if __name__ == "__main__":
    main()