# data_loader.py
import json
import os

def load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_pokemon_with_id(pokemon_id: str):
    data = load_json("data/pokemon.json")
    if pokemon_id in data:
        pokemon = data[pokemon_id]
        pokemon["id"] = pokemon_id
        return pokemon
    return None