# data/moves_loader.py

"""
Charge et fournit l'accès aux données des attaques (moves.json).
Inclut des fonctions utilitaires pour récupérer des informations sur les attaques.
"""

import json
import os
from functools import lru_cache

MOVES_PATH = os.path.join("data", "moves.json")

@lru_cache
def load_moves_data():
    """Charge toutes les attaques depuis le fichier JSON (avec mise en cache)."""
    with open(MOVES_PATH, encoding="utf-8") as f:
        return json.load(f)

def patch_move_data(move: dict, language: str = "fr") -> dict:
    """
    Corrige et complète les champs nécessaires pour éviter les erreurs d'UI ou de logique.

    Args:
        move (dict): Données de l'attaque.
        language (str): Langue utilisée (par défaut "fr").

    Returns:
        dict: Attaque patchée.
    """
    if move is None:
        return None

    # Fallback pour les interfaces anglophones
    if "name" not in move and "name_fr" in move:
        move["name"] = move["name_fr"]

    # Capitalise le nom français
    if language == "fr" and "name_fr" in move:
        move["name_fr"] = move["name_fr"].capitalize()

    # Ajoute max_pp si manquant
    if "pp" in move and "max_pp" not in move:
        move["max_pp"] = move["pp"]

    return move

def get_move_by_id(move_id: int) -> dict:
    """
    Récupère une attaque par son identifiant.

    Args:
        move_id (int): ID de l'attaque.

    Returns:
        dict: Attaque correspondante ou None.
    """
    moves = load_moves_data()
    move = next((m for m in moves if m["id"] == move_id), None)
    return patch_move_data(move)

def get_move_by_name(move_name: str, language: str = "en") -> dict:
    """
    Récupère une attaque par son nom (anglais ou français).

    Args:
        move_name (str): Nom de l'attaque.
        language (str): Langue à utiliser ("en" ou "fr").

    Returns:
        dict: Attaque trouvée ou None.
    """
    moves = load_moves_data()
    key = "name_fr" if language == "fr" else "name"

    for move in moves:
        if move.get(key, "").lower() == move_name.lower():
            return patch_move_data(move, language=language)

    return None

def get_move_type(move_name: str) -> str:
    """
    Retourne le type de l'attaque.

    Args:
        move_name (str): Nom de l'attaque.

    Returns:
        str: Type (ex: "Feu", "Eau", etc.) ou None.
    """
    move = get_move_data(move_name)
    return move.get("type") if move else None

def get_move_power(move_name: str) -> int:
    """Retourne la puissance de l'attaque."""
    move = get_move_data(move_name)
    return move.get("power") if move else None

def get_move_accuracy(move_name: str) -> int:
    """Retourne la précision de l'attaque."""
    move = get_move_data(move_name)
    return move.get("accuracy") if move else None

def get_move_pp(move_name: str) -> int:
    """Retourne les PP de l'attaque."""
    move = get_move_data(move_name)
    return move.get("pp") if move else None

def get_move_description(move_name: str) -> str:
    """Retourne la description française de l'attaque."""
    move = get_move_data(move_name)
    return move.get("description") if move else None

def get_move_data(move_name: str) -> dict:
    """
    Alias vers get_move_by_name en français (compatibilité par défaut).

    Args:
        move_name (str): Nom français de l'attaque.

    Returns:
        dict: Données complètes de l'attaque.
    """
    return get_move_by_name(move_name, language="fr")
