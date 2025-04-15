import os, json, requests
from tqdm import tqdm

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

def generate_moves_data():
    moves = {}
    res = requests.get("https://pokeapi.co/api/v2/move?limit=1000")
    if res.status_code != 200:
        return

    for entry in tqdm(res.json()["results"], desc="📥 Moves"):
        r = requests.get(entry["url"])
        if r.status_code != 200:
            continue
        data = r.json()

        name_fr = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), data["name"].title())
        moves[name_fr] = {
            "type": data["type"]["name"].capitalize(),
            "category": data["damage_class"]["name"].capitalize(),
            "power": data["power"] or 0,
            "accuracy": data["accuracy"] or 100,
            "pp": data["pp"] or 0
        }

    with open(os.path.join(DATA, "moves.json"), "w", encoding="utf-8") as f:
        json.dump(moves, f, indent=2)
