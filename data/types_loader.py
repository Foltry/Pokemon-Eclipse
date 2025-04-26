import json
import os

TYPES_PATH = os.path.join("data", "types.json")

def get_type_index(type_name: str) -> int:
    """
    Retourne l'index vertical d'un type donné (0 = Normal, 1 = Combat, ...),
    selon le fichier types.json localisé en français.
    """
    with open(TYPES_PATH, encoding="utf-8") as f:
        types = json.load(f)

    for i, t in enumerate(types):
        if t["name"].lower() == type_name.lower():
            return i
    return 0  # Valeur par défaut si type non trouvé
