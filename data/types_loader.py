# core/types_loader.py

import json
import os

TYPES_PATH = os.path.join("data", "types.json")

# Chargement en mémoire dès l'import
with open(TYPES_PATH, encoding="utf-8") as f:
    _types_data = json.load(f)

def get_all_types() -> list:
    """Retourne la liste complète des types."""
    return _types_data

def get_type_index(type_name: str) -> int:
    """
    Retourne l'index vertical d'un type donné (0 = Normal, 1 = Combat, ...),
    selon l'ordre du fichier types.json.
    """
    for i, type_info in enumerate(_types_data):
        if type_info["name"].lower() == type_name.lower():
            return i
    return 0  # Valeur par défaut si non trouvé

def get_type_relations(type_name: str) -> dict:
    """
    Retourne les relations de dégâts du type spécifié.
    (damage_relations : double_damage_from, half_damage_from, no_damage_from, etc.)
    """
    for type_info in _types_data:
        if type_info["name"].lower() == type_name.lower():
            return type_info.get("damage_relations", {})
    return {}

def get_type_color(type_name: str) -> str:
    """
    (Optionnel) Retourne une couleur associée au type si disponible dans types.json,
    sinon renvoie une couleur par défaut (par exemple "#FFFFFF").
    """
    for type_info in _types_data:
        if type_info["name"].lower() == type_name.lower():
            return type_info.get("color", "#FFFFFF")
    return "#FFFFFF"

def get_type_english_name(type_name: str) -> str:
    """
    (Optionnel) Si types.json contient aussi le nom anglais,
    cette fonction le retourne.
    """
    for type_info in _types_data:
        if type_info["name"].lower() == type_name.lower():
            return type_info.get("english_name", type_info["name"])
    return type_name
