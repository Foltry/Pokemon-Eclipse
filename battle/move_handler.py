# battle/move_handler.py

import random
from battle.move_effects import apply_move_effect
from battle.move_utils import (
    check_accuracy,
    is_protected,
    should_fail,
    process_multi_hit,
    get_fixed_damage,
    reset_temp_status,
)
from data.moves_loader import get_move_by_name

def use_move(attacker, defender, move):
    """
    Traite l'utilisation d'une capacité, infligeant les dégâts et appliquant les effets secondaires.

    Args:
        attacker (dict): Le Pokémon attaquant.
        defender (dict): Le Pokémon défenseur.
        move (dict): Données de l'attaque (doit contenir au minimum "name").

    Returns:
        dict: {"damage": int, "messages": list[str], "deferred_damage": Optional[int]}
    """
    messages = []
    deferred_damage = None

    move = get_move_by_name(move["name"], language="fr") or move
    print(f"[DEBUG] Utilisation de {move.get('name', move.get('name_fr', '???'))}")

    if should_fail(attacker, defender, move):
        messages.append(f"L'attaque de {attacker['name']} a échoué.")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages, "deferred_damage": None}

    if not check_accuracy(attacker, defender, move):
        messages.append(f"{attacker['name']} rate son attaque !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages, "deferred_damage": None}

    if is_protected(defender):
        messages.append(f"{defender['name']} s'est protégé contre l'attaque !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages, "deferred_damage": None}

    if move.get("effects", {}).get("one_hit_ko"):
        defender["hp"] = 0
        messages.append(f"{attacker['name']} a mis KO {defender['name']} en un seul coup !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 9999, "messages": messages, "deferred_damage": 9999}

    damage = 0

    if move.get("power") or move.get("fixed_damage") or move.get("level_damage"):
        damage_info = calculate_basic_damage(attacker, defender, move)

        if isinstance(damage_info, tuple):
            damage, extra_messages = damage_info
            messages.extend(extra_messages)
        else:
            damage = damage_info

        damage = max(1, damage)
        deferred_damage = damage
        messages.append(f"{attacker['name']} utilise {move['name_fr']} !")
        messages.append(f"{defender['name']} a subi {damage} dégâts !")

        secondary_effects = apply_move_effect(attacker, defender, move, last_damage=damage)
        if secondary_effects:
            messages.extend(secondary_effects)

    else:
        messages.append(f"{attacker['name']} utilise {move['name_fr']} !")

        secondary_effects = apply_move_effect(attacker, defender, move, last_damage=0)

        if secondary_effects:
            messages.extend(secondary_effects)
        else:
            messages.append("Mais cela n'a eu aucun effet...")

    reset_temp_status(attacker)
    reset_temp_status(defender)

    return {
        "damage": damage,
        "messages": messages,
        "deferred_damage": deferred_damage
    }

def calculate_basic_damage(attacker, defender, move):
    """
    Calcule les dégâts d'une attaque de base (sans effets secondaires).

    Args:
        attacker (dict): Pokémon attaquant.
        defender (dict): Pokémon défenseur.
        move (dict): Attaque utilisée.

    Returns:
        int | tuple[int, list[str]]: Dégâts infligés, ou (1, messages) pour attaques multi-coups.
    """
    fixed_damage = get_fixed_damage(attacker, defender, move)
    if fixed_damage is not None:
        return fixed_damage

    if move.get("multi_hit"):
        multi_hit_info = process_multi_hit(attacker, defender, move)
        return 1, multi_hit_info["messages"]

    attack_stat = attacker.get("stats", {}).get("atk", 10)
    defense_stat = defender.get("stats", {}).get("def", 10)
    level = attacker.get("level", 5)
    power = move.get("power", 50)

    base_damage = (((2 * level / 5 + 2) * attack_stat * power) / (defense_stat * 50)) + 2
    base_damage *= random.uniform(0.85, 1.0)

    return int(base_damage)
