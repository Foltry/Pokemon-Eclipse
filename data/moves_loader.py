# data/moves_loader.py

import json
import os

MOVES_PATH = os.path.join("data", "moves.json")

def load_moves_data():
    with open(MOVES_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_move_by_id(move_id: int) -> dict:
    """
    Retourne un mouvement à partir de son ID.
    """
    moves = load_moves_data()
    return next((move for move in moves if move["id"] == move_id), None)

def get_move_by_name(move_name: str) -> dict:
    """
    Retourne un mouvement à partir de son nom français.
    """
    moves = load_moves_data()
    return next((move for move in moves if move["name_fr"].lower() == move_name.lower()), None)

def get_move_type(move_name: str) -> str:
    """
    Retourne le type d'un mouvement donné (en anglais).
    """
    move = get_move_by_name(move_name)
    return move["type"] if move else None

def get_move_power(move_name: str) -> int:
    """
    Retourne la puissance d'un mouvement donné.
    """
    move = get_move_by_name(move_name)
    return move["power"] if move else None

def get_move_accuracy(move_name: str) -> int:
    """
    Retourne la précision d'un mouvement donné.
    """
    move = get_move_by_name(move_name)
    return move["accuracy"] if move else None

def get_move_pp(move_name: str) -> int:
    """
    Retourne les PP de base d'un mouvement donné.
    """
    move = get_move_by_name(move_name)
    return move["pp"] if move else None

def get_move_description(move_name: str) -> str:
    """
    Retourne la description française d'un mouvement donné.
    """
    move = get_move_by_name(move_name)
    return move["description"] if move else None
