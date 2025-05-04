# data/types_loader.py

"""
Fournit des fonctions utilitaires pour interagir avec les données de types Pokémon.
Charge automatiquement types.json en mémoire.
"""

import json
import os

TYPES_PATH = os.path.join("data", "types.json")

# Chargement en mémoire dès l'import pour améliorer les performances
with open(TYPES_PATH, encoding="utf-8") as f:
    _types_data = json.load(f)


def get_all_types() -> list:
    """Retourne la liste complète des types (dicts)."""
    return _types_data


def get_type_index(type_name: str) -> int:
    """
    Retourne l’index du type dans la liste (utile pour afficher l’icône correcte).

    Args:
        type_name (str): Nom du type à chercher.

    Returns:
        int: Index dans la liste ou 0 si non trouvé.
    """
    return next((i for i, t in enumerate(_types_data) if t["name"].lower() == type_name.lower()), 0)


def get_type_relations(type_name: str) -> dict:
    """
    Retourne les relations de dégâts du type (double_damage_from, etc.).

    Args:
        type_name (str): Nom du type.

    Returns:
        dict: Dictionnaire des relations ou {} si non trouvé.
    """
    return next((t.get("damage_relations", {}) for t in _types_data if t["name"].lower() == type_name.lower()), {})


def get_type_color(type_name: str) -> str:
    """
    Retourne la couleur associée au type (s'il y en a une).

    Args:
        type_name (str): Nom du type.

    Returns:
        str: Code couleur hexadécimal ou "#FFFFFF" par défaut.
    """
    return next((t.get("color", "#FFFFFF") for t in _types_data if t["name"].lower() == type_name.lower()), "#FFFFFF")


def get_type_english_name(type_name: str) -> str:
    """
    Retourne le nom anglais du type (si défini dans le JSON).

    Args:
        type_name (str): Nom français.

    Returns:
        str: Nom anglais ou nom original si non défini.
    """
    return next((t.get("english_name", t["name"]) for t in _types_data if t["name"].lower() == type_name.lower()), type_name)
