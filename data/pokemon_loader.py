# core/pokemon_loader.py

import json
import os
from data.moves_loader import get_move_by_name

POKEMON_PATH = os.path.join("data", "pokemon.json")

def load_pokemon_data():
    """Charge tout le fichier pokemon.json en mémoire."""
    with open(POKEMON_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_pokemon_by_id(pokemon_id: int) -> dict:
    """Retourne un Pokémon à partir de son ID numérique."""
    data = load_pokemon_data()
    for pokemon in data:
        if pokemon["id"] == pokemon_id:
            return pokemon
    return {}

def get_pokemon_by_name(name: str) -> dict:
    """Retourne un Pokémon à partir de son nom (case insensitive)."""
    data = load_pokemon_data()
    for pokemon in data:
        if pokemon["name"].lower() == name.lower():
            return pokemon
    return {}

def get_pokemon_stats(pokemon_id: int) -> dict:
    """Retourne les statistiques d'un Pokémon par son ID."""
    pokemon = get_pokemon_by_id(pokemon_id)
    return pokemon.get("stats", {})

def get_pokemon_types(pokemon_id: int) -> list:
    """Retourne la liste des types d'un Pokémon par son ID."""
    pokemon = get_pokemon_by_id(pokemon_id)
    return pokemon.get("types", [])

def get_pokemon_moves(pokemon_id: int) -> list:
    """Retourne la liste des attaques connues d'un Pokémon."""
    pokemon = get_pokemon_by_id(pokemon_id)
    return pokemon.get("moves", [])

def get_pokemon_sprite(pokemon_id: int, form: str = "front") -> str:
    """
    Retourne le chemin du sprite d'un Pokémon.
    form peut être : front, back, front_shiny, back_shiny, front_female, etc.
    """
    pokemon = get_pokemon_by_id(pokemon_id)
    sprites = pokemon.get("sprites", {})
    return sprites.get(form, "")

def get_pokemon_base_experience(pokemon_id: int) -> int:
    """Retourne l'expérience de base gagnée en battant ce Pokémon."""
    pokemon = get_pokemon_by_id(pokemon_id)
    return pokemon.get("base_experience", 0)

def get_pokemon_evolution_chain(pokemon_id: int) -> dict:
    """Retourne l'arbre d'évolution à partir du Pokémon donné."""
    pokemon = get_pokemon_by_id(pokemon_id)
    return pokemon.get("evolution", {})

def get_all_pokemon() -> list:
    """
    Retourne la liste complète des Pokémon du fichier JSON.
    """
    with open(POKEMON_PATH, encoding="utf-8") as f:
        return json.load(f)
    
from data.moves_loader import get_move_by_name

def get_learnable_moves(pokemon_id: int, level: int = 5) -> list:
    """
    Retourne une liste de mouvements que le Pokémon peut apprendre à son niveau.
    """
    pokemon = get_pokemon_by_id(pokemon_id)
    if not pokemon:
        return []

    moves = []
    learnset = pokemon.get("moves", [])  # Attention ici "moves", pas "learnset"

    for move_entry in learnset:
        if move_entry["level"] <= level:
            move_data = get_move_by_name(move_entry["name"], language="fr")  # Important: language="fr"
            if move_data:
                move = {
                    "name": move_data["name_fr"],
                    "type": move_data["type"],
                    "power": move_data["power"],
                    "accuracy": move_data["accuracy"],
                    "category": move_data["damage_class"],
                    "pp": move_data["pp"],
                    "max_pp": move_data["pp"],
                }
                moves.append(move)

    return moves[:4]