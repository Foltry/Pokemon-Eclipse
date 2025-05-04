# core/data_loader.py

"""
Fonctions utilitaires pour la gestion des fichiers JSON et des chemins.
"""

import json
import os

def load_json(path: str) -> dict:
    """
    Charge un fichier JSON depuis un chemin donné.

    Args:
        path (str): Chemin vers le fichier JSON.

    Returns:
        dict: Contenu du fichier JSON.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(path: str, data: dict):
    """
    Sauvegarde un dictionnaire Python dans un fichier JSON.

    Args:
        path (str): Chemin de destination du fichier JSON.
        data (dict): Données à enregistrer.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ensure_dir(path: str):
    """
    Crée un dossier s'il n'existe pas encore.

    Args:
        path (str): Chemin du dossier à créer.
    """
    os.makedirs(path, exist_ok=True)

def file_exists(path: str) -> bool:
    """
    Vérifie si un fichier existe.

    Args:
        path (str): Chemin du fichier.

    Returns:
        bool: True si le fichier existe, False sinon.
    """
    return os.path.exists(path)
