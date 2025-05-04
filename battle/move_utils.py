# battle/move_utils.py

import random

def check_accuracy(attacker, defender, move):
    """
    Vérifie si l'attaque réussit selon sa précision.

    Args:
        attacker (dict): Le Pokémon attaquant.
        defender (dict): Le Pokémon défenseur.
        move (dict): Les données du mouvement.

    Returns:
        bool: True si l'attaque touche, False sinon.
    """
    accuracy = move.get("accuracy")
    if accuracy is None:
        return True  # Certaines attaques (ex : Danse-Lames) ne peuvent pas échouer
    return random.randint(1, 100) <= accuracy

def is_protected(defender):
    """
    Vérifie si la cible est sous un effet de protection.

    Args:
        defender (dict): Le Pokémon défenseur.

    Returns:
        bool: True si protégé par Abri/Détection/etc.
    """
    return defender.get("_protected", False)

def should_fail(attacker, defender, move, last_move=None):
    """
    Détermine si l'attaque doit échouer directement.

    Args:
        attacker (dict): Le Pokémon attaquant.
        defender (dict): Le Pokémon défenseur.
        move (dict): Le mouvement utilisé.
        last_move (dict, optional): Dernier mouvement utilisé (non utilisé ici).

    Returns:
        bool: True si l'attaque échoue immédiatement.
    """
    if attacker.get("_recharging"):
        attacker["_recharging"] = False
        return True
    if move.get("requires_charge") and not attacker.get("_charging"):
        return True
    if move.get("name") == "Échec":
        return True
    return False

def process_multi_hit(attacker, defender, move_data):
    """
    Gère les attaques à coups multiples (ex: Furia, Double-Pied).

    Args:
        attacker (dict): Le Pokémon attaquant.
        defender (dict): Le Pokémon défenseur.
        move_data (dict): Les données du mouvement.

    Returns:
        dict: {"hits": int, "messages": list[str]}
    """
    hits = random.choices([2, 3, 4, 5], weights=[35, 35, 15, 15])[0]
    messages = [f"Le coup {i + 1} touche !" for i in range(hits)]
    messages.append(f"{move_data['name']} a frappé {hits} fois !")

    return {"hits": hits, "messages": messages}

def get_fixed_damage(attacker, defender, move):
    """
    Retourne les dégâts fixes pour certaines attaques spéciales.

    Args:
        attacker (dict): Le Pokémon attaquant.
        defender (dict): Le Pokémon défenseur.
        move (dict): Les données de l'attaque.

    Returns:
        int | None: Dégâts fixes ou None si non applicable.
    """
    if move.get("fixed_damage") is not None:
        return move["fixed_damage"]
    if move.get("level_damage"):
        return attacker.get("level", 1)
    return None

def reset_temp_status(pokemon):
    """
    Réinitialise les états temporaires d'un Pokémon après son tour.

    Args:
        pokemon (dict): Données du Pokémon à nettoyer.
    """
    pokemon.pop("_protected", None)
    pokemon.pop("_flinched", None)
