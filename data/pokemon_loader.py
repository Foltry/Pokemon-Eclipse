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
    Retourne une liste de mouvements que le Pokémon peut apprendre jusqu'à son niveau donné.
    Corrige la gestion des doublons et des attaques invalides.
    """
    pokemon = get_pokemon_by_id(pokemon_id)
    if not pokemon:
        return []

    moves = []
    seen_moves = set()
    learnset = pokemon.get("moves", [])

    # Trier par niveau croissant pour récupérer les meilleures versions
    learnset = sorted(learnset, key=lambda x: x["level"])

    for move_entry in learnset:
        move_name = move_entry["name"]

        if move_entry["level"] <= level and move_name not in seen_moves:
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

    return moves[:4]  # Limite à 4 attaques


def get_pokemon_by_id_name(name: str) -> dict:
    """Alias pour get_pokemon_by_name (utilisé pour compatibilité dans le code)."""
    return get_pokemon_by_name(name)
