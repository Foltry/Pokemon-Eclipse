# battle/engine.py

import random
from data.types_loader import get_all_types

TYPE_CHART = get_all_types()

def find_type_info(type_name):
    for type_info in TYPE_CHART:
        if type_info["name"].lower() == type_name.lower():
            return type_info
    return None

def get_type_multiplier(move_type, defender_types):
    multiplier = 1.0
    move_info = find_type_info(move_type)
    if not move_info:
        return multiplier

    relations = move_info.get("damage_relations", {})

    for target_type in defender_types:
        if target_type in relations.get("double_damage_to", []):
            multiplier *= 2.0
        elif target_type in relations.get("half_damage_to", []):
            multiplier *= 0.5
        elif target_type in relations.get("no_damage_to", []):
            multiplier *= 0.0
    return multiplier

def calculate_damage(attacker, defender, move):
    atk_level = attacker.get("level", 5)
    move_power = move.get("power")
    if move_power is None or move_power == 0:
        return 0, False, 1.0

    is_special = move.get("damage_class") == "special"

    atk_stat = attacker["stats"].get("special-attack" if is_special else "attack", 10)
    def_stat = defender["stats"].get("special-defense" if is_special else "defense", 10)

    base_damage = (((2 * atk_level / 5 + 2) * move_power * atk_stat / def_stat) / 50) + 2

    move_type = move.get("type")
    stab = 1.5 if move_type in attacker.get("types", []) else 1.0
    type_multiplier = get_type_multiplier(move_type, defender.get("types", []))
    is_crit = random.random() < 0.0625
    crit_multiplier = 1.5 if is_crit else 1.0
    rand = random.uniform(0.85, 1.0)

    damage = int(base_damage * stab * type_multiplier * crit_multiplier * rand)
    return max(1, damage), is_crit, type_multiplier
