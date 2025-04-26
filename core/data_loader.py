# core/data_loader.py

import json
import os

def load_json(path: str) -> dict:
    """Charge un fichier JSON depuis un chemin."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(path: str, data: dict):
    """Sauvegarde un dictionnaire Python dans un fichier JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ensure_dir(path: str):
    """Crée un dossier si nécessaire."""
    os.makedirs(path, exist_ok=True)

def file_exists(path: str) -> bool:
    """Vérifie si un fichier existe."""
    return os.path.exists(path)
