import json
import os


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def load_pokemon_with_id(pokemon_id: str):
    data = load_json("data/pokemon.json")
    if pokemon_id in data:
        pokemon = data[pokemon_id]
        pokemon["id"] = pokemon_id
        return pokemon
    return None
