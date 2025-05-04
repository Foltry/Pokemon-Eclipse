# data/items_loader.py

"""
Chargeur d'objets depuis le fichier items.json.
Contient des fonctions utilitaires pour accéder aux propriétés des objets.
"""

import json
import os
from functools import lru_cache

ITEMS_PATH = os.path.join("data", "items.json")

@lru_cache
def load_items():
    """Charge tous les objets depuis le fichier JSON (avec mise en cache)."""
    with open(ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_item_data(item_name: str) -> dict:
    """
    Retourne toutes les données d'un objet donné.

    Args:
        item_name (str): Nom de l'objet.

    Returns:
        dict: Données de l'objet, ou {} si non trouvé.
    """
    items = load_items()
    return next((item for item in items if item["name"].lower() == item_name.lower()), {})

# Alias pour compatibilité
get_item_by_name = get_item_data

def get_item_effect(item_name: str) -> str:
    """
    Retourne l'effet texte d'un objet.

    Args:
        item_name (str): Nom de l'objet.

    Returns:
        str: Effet texte ou chaîne vide.
    """
    return get_item_data(item_name).get("effect", "")

def get_item_cost(item_name: str) -> int:
    """
    Retourne le coût d'achat d'un objet.

    Args:
        item_name (str): Nom de l'objet.

    Returns:
        int: Prix en Pokédollars.
    """
    return get_item_data(item_name).get("cost", 0)

def get_item_sprite(item_name: str) -> str:
    """
    Retourne le chemin du sprite d’un objet.

    Args:
        item_name (str): Nom de l'objet.

    Returns:
        str: Chemin du sprite ou chaîne vide.
    """
    sprite = get_item_data(item_name).get("sprite")
    return os.path.join("assets", "sprites", "items", sprite) if sprite else ""

def get_item_category(item_name: str) -> str:
    """
    Retourne la catégorie de l'objet (ex: healing, balls...).

    Args:
        item_name (str): Nom de l'objet.

    Returns:
        str: Nom de la catégorie.
    """
    return get_item_data(item_name).get("category", "")

def get_all_items() -> dict:
    """
    Retourne tous les objets sous forme de dictionnaire {nom: données}.

    Returns:
        dict[str, dict]: Tous les objets par nom.
    """
    return {item["name"]: item for item in load_items()}

def list_available_items() -> list:
    """
    Retourne la liste des objets valides pour les récompenses de combat :
    - Doivent avoir un sprite
    - Ne doivent pas être des Master Balls

    Returns:
        list[str]: Noms des objets valides.
    """
    items = get_all_items()
    return [
        name for name, item in items.items()
        if item.get("sprite") and name.lower() != "master ball"
    ]
