import json
import os
from functools import lru_cache

ITEMS_PATH = os.path.join("data", "items.json")

@lru_cache
def load_items():
    with open(ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_item_data(item_name: str) -> dict:
    """Retourne toutes les données d'un objet donné (dict complet)."""
    items = load_items()
    for item in items:
        if item["name"].lower() == item_name.lower():
            return item
    return {}

# Alias pour compatibilité
get_item_by_name = get_item_data

def get_item_effect(item_name: str) -> str:
    """Retourne l'effet texte d'un objet."""
    item = get_item_data(item_name)
    return item.get("effect", "")

def get_item_cost(item_name: str) -> int:
    """Retourne le coût d'achat d'un objet."""
    item = get_item_data(item_name)
    return item.get("cost", 0)

def get_item_sprite(item_name: str) -> str:
    """Retourne le chemin du sprite d'un objet."""
    item = get_item_data(item_name)
    sprite = item.get("sprite")
    if sprite:
        return os.path.join("assets", "sprites", "items", sprite)
    return ""

def get_item_category(item_name: str) -> str:
    """Retourne la catégorie d'un objet (ex: healing, balls, etc.)."""
    item = get_item_data(item_name)
    return item.get("category", "")

def get_all_items() -> dict:
    """Retourne un dictionnaire {nom: données} des objets."""
    with open(ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)
        return {item["name"]: item for item in items}


def list_available_items() -> list:
    """
    Retourne uniquement les objets valides pour les bonus après victoire :
    (exclut les Master Balls et ceux sans sprite)
    """
    items = get_all_items()
    valid_items = [
        name
        for name, item in items.items()
        if item.get("sprite") and name.lower() != "master ball"
    ]
    return valid_items
