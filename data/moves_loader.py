# data/moves_loader.py

import json
import os
from functools import lru_cache

MOVES_PATH = os.path.join("data", "moves.json")

@lru_cache
def load_moves_data():
    with open(MOVES_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_move_by_id(move_id: int) -> dict:
    """Retourne un mouvement à partir de son ID."""
    moves = load_moves_data()
    return next((move for move in moves if move["id"] == move_id), None)

def get_move_by_name(move_name: str, language: str = "en") -> dict:
    """Retourne un mouvement à partir de son nom (anglais ou français)."""
    moves = load_moves_data()
    for move in moves:
        if language == "fr":
            if move.get("name_fr", "").lower() == move_name.lower():
                return move
        else:
            if move.get("name", "").lower() == move_name.lower():
                return move
    return None

def get_move_type(move_name: str) -> str:
    """Retourne le type d'un mouvement donné."""
    move = get_move_data(move_name)
    return move.get("type") if move else None

def get_move_power(move_name: str) -> int:
    """Retourne la puissance d'un mouvement donné."""
    move = get_move_data(move_name)
    return move.get("power") if move else None

def get_move_accuracy(move_name: str) -> int:
    """Retourne la précision d'un mouvement donné."""
    move = get_move_data(move_name)
    return move.get("accuracy") if move else None

def get_move_pp(move_name: str) -> int:
    """Retourne les PP de base d'un mouvement donné."""
    move = get_move_data(move_name)
    return move.get("pp") if move else None

def get_move_description(move_name: str) -> str:
    """Retourne la description française d'un mouvement donné."""
    move = get_move_data(move_name)
    return move.get("description") if move else None

def get_move_data(move_name: str) -> dict:
    """Alias pour get_move_by_name (langue française par défaut ici pour compatibilité)."""
    return get_move_by_name(move_name, language="fr")
