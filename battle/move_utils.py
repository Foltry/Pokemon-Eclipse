import random

def check_accuracy(attacker, defender, move):
    """Renvoie True si l'attaque touche, False sinon."""
    accuracy = move.get("accuracy")
    if accuracy is None:
        return True  # attaques qui ne ratent jamais
    return random.randint(1, 100) <= accuracy

def is_protected(defender):
    """Vérifie si le défenseur est sous Abri ou similaire."""
    return defender.get("_protected", False)

def should_fail(attacker, defender, move, last_move):
    """Détermine si l'attaque échoue pour une autre raison (statut, effet, etc.)."""
    if attacker.get("_recharging"):
        attacker["_recharging"] = False
        return True
    if move.get("requires_charge") and not attacker.get("_charging"):
        return True
    if move.get("name") == "Échec":
        return True
    return False

def get_fixed_damage(attacker, move):
    """Retourne les dégâts fixes définis dans l’effet."""
    value = move["fixed_damage"]
    if value == "level":
        return attacker["level"]
    return int(value)

def process_multi_hit(attacker, defender, move):
    """Gère les attaques frappant plusieurs fois (2 à 5)."""
    from battle.engine import calculate_damage

    hits = random.choices([2, 3, 4, 5], weights=[35, 35, 15, 15])[0]
    total_damage = 0
    any_crit = False
    last_multiplier = 1.0

    for _ in range(hits):
        dmg, is_crit, mult = calculate_damage(attacker, defender, move)
        total_damage += dmg
        any_crit |= is_crit
        last_multiplier = mult

    return hits, total_damage, any_crit, last_multiplier
