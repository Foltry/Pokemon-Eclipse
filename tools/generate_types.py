import os, json, requests
from tqdm import tqdm

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

GEN_1_TO_5_TYPES = [
    "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
    "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon",
    "dark", "steel"
]
GEN_1_TO_5_TYPES_CAP = [t.capitalize() for t in GEN_1_TO_5_TYPES]

def clean_type_list(raw_list):
    return [t.capitalize() for t in raw_list if t.capitalize() in GEN_1_TO_5_TYPES_CAP]

def generate_types_data():
    types = {}

    for t_name in tqdm(GEN_1_TO_5_TYPES, desc="📥 Types (Gen 1-5 only)"):
        res = requests.get(f"https://pokeapi.co/api/v2/type/{t_name}")
        if res.status_code != 200:
            continue
        data = res.json()
        fr_name = next((n["name"] for n in data["names"] if n["language"]["name"] == "fr"), t_name.capitalize())

        types[fr_name] = {
            "weak": clean_type_list([x["name"] for x in data["damage_relations"]["double_damage_from"]]),
            "resist": clean_type_list([x["name"] for x in data["damage_relations"]["half_damage_from"]]),
            "immune": clean_type_list([x["name"] for x in data["damage_relations"]["no_damage_from"]])
        }

    with open(os.path.join(DATA, "types.json"), "w", encoding="utf-8") as f:
        json.dump(types, f, indent=2)
