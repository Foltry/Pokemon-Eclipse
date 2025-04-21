import random
import json
import os

# Chemin vers le fichier types.json
TYPES_PATH = os.path.join("data", "types.json")

with open(TYPES_PATH, encoding="utf-8") as f:
    TYPE_CHART = json.load(f)

def get_type_multiplier(move_type, defender_types):
    multiplier = 1.0
    for target_type in defender_types:
        if target_type not in TYPE_CHART or move_type not in TYPE_CHART:
            continue
        relations = TYPE_CHART[move_type]["damage_relations"]
        if target_type in relations["double_damage_to"]:
            multiplier *= 2.0
        elif target_type in relations["half_damage_to"]:
            multiplier *= 0.5
        elif target_type in relations["no_damage_to"]:
            multiplier *= 0.0
    return multiplier

def calculate_damage(attacker, defender, move):
    # Récupère les données nécessaires
    atk_level = attacker["level"]
    power = move["power"]
    if power is None or power == 0:
        return 0

    is_special = move["damage_class"] == "special"
    atk_stat = attacker["stats"]["sp_atk" if is_special else "atk"]
    def_stat = defender["stats"]["sp_def" if is_special else "def"]

    base_damage = (((2 * atk_level / 5 + 2) * power * atk_stat / def_stat) / 50) + 2

    # Bonus de type (STAB)
    move_type = move["type"]
    stab = 1.5 if move_type in attacker["types"] else 1.0

    # Multiplicateur de type
    target_types = defender["types"]
    type_multiplier = get_type_multiplier(move_type, target_types)

    # Critique
    is_crit = random.random() < 0.0625  # 6.25 %
    crit_multiplier = 1.5 if is_crit else 1.0

    # Random (entre 85% et 100%)
    rand = random.uniform(0.85, 1.0)

    # Total
    damage = int(base_damage * stab * type_multiplier * crit_multiplier * rand)
    return max(1, damage), is_crit, type_multiplier
