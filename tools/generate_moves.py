import os, json, requests, signal, sys

MOVE_PATH = "data/moves.json"

def sig_handler(sig, frame): sys.exit(0)
if hasattr(signal, "SIGTSTP"):
    signal.signal(signal.SIGTSTP, sig_handler)

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f: return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    existing = load_json(MOVE_PATH)
    moves = {}

    url = "https://pokeapi.co/api/v2/move?limit=1000"
    r = requests.get(url)
    if r.status_code != 200: return

    for entry in r.json()["results"]:
        move_data = requests.get(entry["url"]).json()
        mid = str(move_data["id"])
        if mid in existing: continue

        name = next((n["name"] for n in move_data["names"] if n["language"]["name"] == "fr"), move_data["name"])
        print(f"✅ Attaque ajoutée : {name}")
        moves[mid] = {
            "name": name,
            "power": move_data["power"],
            "pp": move_data["pp"],
            "accuracy": move_data["accuracy"],
            "type": move_data["type"]["name"]
        }

    existing.update(moves)
    save_json(MOVE_PATH, existing)
    print(f"✅ {len(moves)} nouvelles attaques ajoutées.")

if __name__ == "__main__":
    main()