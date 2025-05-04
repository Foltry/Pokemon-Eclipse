# data/pokemon_loader.py

"""
Fournit des fonctions pour charger les données des Pokémon à partir de pokemon.json.
Permet l'accès par ID, nom, ou autre champ utile (types, stats, sprites, etc.).
"""

import json
import os
from data.moves_loader import get_move_by_name

POKEMON_PATH = os.path.join("data", "pokemon.json")


def load_pokemon_data() -> list:
    """Charge tout le fichier pokemon.json en mémoire."""
    with open(POKEMON_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_pokemon_by_id(pokemon_id: int) -> dict:
    """Retourne un Pokémon à partir de son ID numérique."""
    return next((p for p in load_pokemon_data() if p["id"] == pokemon_id), {})


def get_pokemon_by_name(name: str) -> dict:
    """Retourne un Pokémon à partir de son nom (insensible à la casse)."""
    return next((p for p in load_pokemon_data() if p["name"].lower() == name.lower()), {})


def get_pokemon_stats(pokemon_id: int) -> dict:
    """Retourne les statistiques d'un Pokémon par son ID."""
    return get_pokemon_by_id(pokemon_id).get("stats", {})


def get_pokemon_types(pokemon_id: int) -> list:
    """Retourne la liste des types d'un Pokémon par son ID."""
    return get_pokemon_by_id(pokemon_id).get("types", [])


def get_pokemon_moves(pokemon_id: int) -> list:
    """Retourne la liste des attaques connues d'un Pokémon."""
    return get_pokemon_by_id(pokemon_id).get("moves", [])


def get_pokemon_sprite(pokemon_id: int, form: str = "front") -> str:
    """
    Retourne le chemin du sprite d'un Pokémon.
    Args:
        form (str): 'front', 'back', 'front_shiny', etc.

    Returns:
        str: chemin du sprite ou chaîne vide.
    """
    return get_pokemon_by_id(pokemon_id).get("sprites", {}).get(form, "")


def get_pokemon_base_experience(pokemon_id: int) -> int:
    """Retourne l'expérience de base gagnée en battant ce Pokémon."""
    return get_pokemon_by_id(pokemon_id).get("base_experience", 0)


def get_pokemon_evolution_chain(pokemon_id: int) -> dict:
    """Retourne l'arbre d'évolution à partir du Pokémon donné."""
    return get_pokemon_by_id(pokemon_id).get("evolution", {})


def get_all_pokemon() -> list:
    """Retourne la liste complète des Pokémon du fichier JSON."""
    return load_pokemon_data()


def get_learnable_moves(pokemon_id: int, level: int = 5) -> list:
    """
    Retourne une liste des mouvements que le Pokémon peut apprendre jusqu'à un certain niveau.

    Args:
        pokemon_id (int): ID du Pokémon.
        level (int): Niveau maximum des attaques à inclure.

    Returns:
        list: Liste de 4 attaques maximum sous forme de dict.
    """
    pokemon = get_pokemon_by_id(pokemon_id)
    if not pokemon:
        return []

    moves = []
    seen_moves = set()

    learnset = sorted(pokemon.get("moves", []), key=lambda x: x["level"])

    for entry in learnset:
        move_name = entry["name"]
        if entry["level"] <= level and move_name not in seen_moves:
            move_data = get_move_by_name(move_name, language="fr")
            if move_data:
                move = {
                    "name": move_data["name_fr"],
                    "type": move_data["type"],
                    "power": move_data.get("power", 0),
                    "accuracy": move_data.get("accuracy", 100),
                    "category": move_data.get("damage_class", "unknown"),
                    "pp": move_data.get("pp", 0),
                    "max_pp": move_data.get("pp", 0),
                }
                moves.append(move)
                seen_moves.add(move_name)
            else:
                print(f"[⚠️] Move introuvable dans moves.json: {move_name} pour Pokémon ID {pokemon_id}")

    return moves[:4]


def get_pokemon_by_id_name(name: str) -> dict:
    """Alias pour get_pokemon_by_name (pour compatibilité avec certaines fonctions)."""
    return get_pokemon_by_name(name)
