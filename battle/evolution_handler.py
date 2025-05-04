# battle/evolution_handler.py

from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves

def check_evolution(pokemon):
    """
    Vérifie si le Pokémon peut évoluer en fonction de son niveau.

    Args:
        pokemon (dict): Données du Pokémon.

    Returns:
        dict | None: Nouvelles données du Pokémon après évolution ou None si aucune.
    """
    evolution_tree = get_evolution_tree(pokemon)
    current_level = pokemon.get("level", 1)

    for evo in evolution_tree:
        evo_level = evo.get("level")
        if evo_level and current_level >= evo_level:
            evolved_data = get_pokemon_by_id_name(evo["species"])
            if evolved_data:
                return evolved_data
    return None

def get_evolution_tree(pokemon):
    """
    Extrait la chaîne d’évolution pour le Pokémon donné.

    Args:
        pokemon (dict): Données du Pokémon.

    Returns:
        list[dict]: Liste d'évolutions possibles.
    """
    def search_evo_chain(evo_data, target_species):
        if evo_data["species"].lower() == target_species:
            return evo_data.get("evolves_to", [])
        for child in evo_data.get("evolves_to", []):
            result = search_evo_chain(child, target_species)
            if result is not None:
                return result
        return None

    base_data = get_pokemon_by_id(pokemon["id"])
    evo_tree = base_data.get("evolution", {})
    return search_evo_chain(evo_tree, base_data["name"].lower()) or []

def get_pokemon_by_id_name(name):
    """
    Recherche un Pokémon dans la base à partir de son nom (anglais, minuscule).

    Args:
        name (str): Nom interne du Pokémon (ex: "ivysaur").

    Returns:
        dict | None: Données du Pokémon ou None si introuvable.
    """
    from data.pokemon_loader import get_all_pokemon
    return next((poke for poke in get_all_pokemon() if poke["name"].lower() == name.lower()), None)

def check_and_apply_evolution(pokemon):
    """
    Applique l'évolution si elle est possible au niveau actuel du Pokémon.

    Args:
        pokemon (dict): Données modifiables du Pokémon.

    Returns:
        dict | None: Nouvelles données du Pokémon si évolution, sinon None.
    """
    evolved_data = check_evolution(pokemon)
    if evolved_data:
        pokemon["id"] = evolved_data["id"]
        pokemon["name"] = evolved_data["name"]
        pokemon["base_stats"] = evolved_data["stats"]
        pokemon["stats"] = evolved_data["stats"].copy()
        pokemon["types"] = evolved_data.get("types", [])
        pokemon["sprites"] = evolved_data.get("sprites", {})

        learnset = get_learnable_moves(pokemon["id"], pokemon["level"])
        for new_move in learnset:
            if all(m["name"] != new_move["name"] for m in pokemon["moves"]):
                if len(pokemon["moves"]) < 4:
                    pokemon["moves"].append(new_move)

        return evolved_data
    return None
