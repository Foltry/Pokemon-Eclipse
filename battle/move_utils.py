# battle/move_utils.py

import random

def check_accuracy(attacker, defender, move):
    """Vérifie si l'attaque touche, selon sa précision."""
    accuracy = move.get("accuracy")
    if accuracy is None:
        return True  # Certaines attaques (ex : Danse-Lames) ne ratent jamais
    return random.randint(1, 100) <= accuracy

def is_protected(defender):
    """Renvoie True si la cible est sous un effet de protection (Abri, Détection, etc.)."""
    return defender.get("_protected", False)

def should_fail(attacker, defender, move, last_move=None):
    """Détermine si l'attaque échoue directement (recharge, attaque spéciale, etc.)."""
    if attacker.get("_recharging"):
        attacker["_recharging"] = False
        return True
    if move.get("requires_charge") and not attacker.get("_charging"):
        return True
    if move.get("name") == "Échec":
        return True
    return False

def process_multi_hit(attacker, defender, move_data):
    """Gère les attaques à frappes multiples (ex: Furia, Double-Pied)."""
    messages = []
    hits = random.choices([2, 3, 4, 5], weights=[35, 35, 15, 15])[0]  # Probabilités officielles

    for i in range(hits):
        messages.append(f"Le coup {i+1} touche !")

    messages.append(f"{move_data['name']} a frappé {hits} fois !")

    return {
        "hits": hits,
        "messages": messages
    }

def get_fixed_damage(attacker, defender, move):
    """Retourne les dégâts fixes si l'attaque suit ce modèle (ex: Sonic Boom, Niveau 5)."""
    if move.get("fixed_damage") is not None:
        return move["fixed_damage"]
    if move.get("level_damage"):
        return attacker.get("level", 1)
    return None

def reset_temp_status(pokemon):
    """Reset les états temporaires d'un Pokémon après son tour."""
    if "_protected" in pokemon:
        del pokemon["_protected"]
    if "_flinched" in pokemon:
        del pokemon["_flinched"]
