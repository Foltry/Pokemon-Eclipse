import os, json, requests, signal, sys

POKE_PATH = "data/pokemon.json"
SPRITE_DIR = "assets/sprites/pokemon/front"

def sig_handler(sig, frame): sys.exit(0)
if hasattr(signal, "SIGTSTP"):
    signal.signal(signal.SIGTSTP, sig_handler)

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f: return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def download_sprite(pid, url):
    path = os.path.join(SPRITE_DIR, f"{pid}.gif")
    if os.path.exists(path): return
    r = requests.get(url)
    if r.status_code == 200:
        with open(path, "wb") as f: f.write(r.content)

def main():
    os.makedirs(SPRITE_DIR, exist_ok=True)
    existing = load_json(POKE_PATH)
    updated = {}

    for pid in range(1, 152):
        pid_str = str(pid).zfill(3)
        if pid_str in existing: continue

        url = f"https://pokeapi.co/api/v2/pokemon/{pid}/"
        r = requests.get(url)
        if r.status_code != 200: continue

        data = r.json()
        name = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"])
        sprite = data["sprites"]["versions"]["generation-v"]["black-white"]["animated"]["front_default"]

        print(f"⬇️ Sprite Pokémon : {pid_str} - {name}")
        download_sprite(pid_str, sprite)

        print(f"✅ Pokémon ajouté : {name}")
        updated[pid_str] = {
            "name": name,
            "types": [t["type"]["name"] for t in data["types"]],
            "base_hp": data["stats"][0]["base_stat"],
            "base_attack": data["stats"][1]["base_stat"],
            "base_defense": data["stats"][2]["base_stat"],
            "moves": [m["move"]["name"] for m in data["moves"][:4]]
        }

    existing.update(updated)
    save_json(POKE_PATH, existing)
    print(f"✅ {len(updated)} nouveaux Pokémon ajoutés.")

if __name__ == "__main__":
    main()