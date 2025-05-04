# battle/use_item.py

from data.items_loader import get_item_category

def use_item_on_pokemon(item_name, pokemon):
    """
    Utilise un objet spécifique sur un Pokémon.

    Args:
        item_name (str): Nom de l'objet.
        pokemon (dict): Données du Pokémon ciblé.

    Returns:
        dict: Contient le succès de l'action et un message utilisateur.
    """
    if not pokemon:
        return {"success": False, "message": "Aucun Pokémon sélectionné."}

    category = get_item_category(item_name)

    if category in ("standard-balls",):
        return {"success": False, "message": "Vous ne pouvez pas utiliser une Poké Ball sur un Pokémon allié !"}

    if category == "healing":
        return apply_healing(item_name, pokemon)

    if category == "status-cures":
        return apply_status_cure(item_name, pokemon)

    return {"success": False, "message": "Objet inutilisable ici."}

def apply_healing(item_name, pokemon):
    """
    Applique un objet de soin à un Pokémon.

    Args:
        item_name (str): Nom de l'objet.
        pokemon (dict): Données du Pokémon.

    Returns:
        dict: Succès et message utilisateur.
    """
    heal_values = {
        "Potion": 20,
        "Super Potion": 50,
        "Hyper Potion": 200,
        "Eau Fraîche": 50,
        "Potion Max": "full",
        "Guérison": "full"
    }

    heal_amount = heal_values.get(item_name)
    if heal_amount is None:
        return {"success": False, "message": "Cet objet de soin n'est pas reconnu."}

    current_hp = pokemon.get("hp", 0)
    max_hp = pokemon.get("stats", {}).get("hp", 100)

    if current_hp >= max_hp:
        return {"success": False, "message": f"{pokemon['name']} a déjà tous ses PV."}

    if heal_amount == "full":
        heal_done = max_hp - current_hp
        pokemon["hp"] = max_hp
    else:
        new_hp = min(current_hp + heal_amount, max_hp)
        heal_done = new_hp - current_hp
        pokemon["hp"] = new_hp

    if item_name == "Guérison":
        pokemon["status"] = None

    return {"success": True, "message": f"{pokemon['name']} récupère {heal_done} PV !"}

def apply_status_cure(item_name, pokemon):
    """
    Applique un objet de soin de statut à un Pokémon.

    Args:
        item_name (str): Nom de l'objet.
        pokemon (dict): Données du Pokémon.

    Returns:
        dict: Succès et message utilisateur.
    """
    if not pokemon.get("status"):
        return {"success": False, "message": f"{pokemon['name']} n'a aucun problème de statut."}

    status_effects = {
        "Antidote": "poison",
        "Anti-Brûle": "burn",
        "Antigel": "freeze",
        "Réveil": "sleep",
        "Anti-Para": "paralysis",
        "Total Soin": "all"
    }

    target_status = status_effects.get(item_name)
    current_status = pokemon.get("status")

    if target_status == "all":
        pokemon["status"] = None
        return {"success": True, "message": f"{pokemon['name']} est totalement guéri !"}

    if current_status == target_status:
        pokemon["status"] = None
        return {"success": True, "message": f"{pokemon['name']} est guéri de {current_status} !"}

    return {"success": False, "message": f"L'objet n'a aucun effet sur {pokemon['name']}."}
