import json
import os
from functools import lru_cache

MOVES_PATH = os.path.join("data", "moves.json")

@lru_cache
def load_moves_data():
    with open(MOVES_PATH, encoding="utf-8") as f:
        return json.load(f)

def patch_move_data(move: dict, language: str = "fr") -> dict:
    """Ajoute les champs nécessaires pour éviter les erreurs dans l'UI et le combat."""
    if move is None:
        return None

    # Ajoute 'name' à partir de name_fr pour les interfaces
    if "name" not in move and "name_fr" in move:
        move["name"] = move["name_fr"]

    # Capitalise le nom (utile pour get_by_name)
    if language == "fr" and "name_fr" in move:
        move["name_fr"] = move["name_fr"].capitalize()

    # Ajoute max_pp si manquant
    if "pp" in move and "max_pp" not in move:
        move["max_pp"] = move["pp"]

    return move

def get_move_by_id(move_id: int) -> dict:
    moves = load_moves_data()
    move = next((move for move in moves if move["id"] == move_id), None)
    return patch_move_data(move)

def get_move_by_name(move_name: str, language: str = "en") -> dict:
    moves = load_moves_data()
    for move in moves:
        if language == "fr":
            if move.get("name_fr", "").lower() == move_name.lower():
                return patch_move_data(move, language="fr")
        else:
            if move.get("name", "").lower() == move_name.lower():
                return patch_move_data(move, language="en")
    return None

def get_move_type(move_name: str) -> str:
    move = get_move_data(move_name)
    return move.get("type") if move else None

def get_move_power(move_name: str) -> int:
    move = get_move_data(move_name)
    return move.get("power") if move else None

def get_move_accuracy(move_name: str) -> int:
    move = get_move_data(move_name)
    return move.get("accuracy") if move else None

def get_move_pp(move_name: str) -> int:
    move = get_move_data(move_name)
    return move.get("pp") if move else None

def get_move_description(move_name: str) -> str:
    move = get_move_data(move_name)
    return move.get("description") if move else None

def get_move_data(move_name: str) -> dict:
    return get_move_by_name(move_name, language="fr")
