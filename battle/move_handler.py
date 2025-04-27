from battle.move_effects import apply_move_effect
from data.moves_loader import get_move_data
from battle.move_utils import (
    check_accuracy,
    is_protected,
    should_fail,
    process_multi_hit,
    get_fixed_damage,
    reset_temp_status,  # 💥 Nouveau import ici
)
import random

def use_move(attacker, defender, move):
    """Traite l'utilisation d'une capacité (dégâts + effets secondaires)."""
    messages = []

    # 1️⃣ Vérifie si l'attaque échoue automatiquement
    if should_fail(attacker, defender, move):
        messages.append(f"L'attaque de {attacker['name']} a échoué.")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages}

    # 2️⃣ Vérifie précision
    if not check_accuracy(attacker, defender, move):
        messages.append(f"{attacker['name']} rate son attaque !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages}

    # 3️⃣ Vérifie Abri / Protection
    if is_protected(defender):
        messages.append(f"{defender['name']} s'est protégé contre l'attaque !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 0, "messages": messages}

    # 4️⃣ Vérifie One-Hit KO
    if move.get("effects", {}).get("one_hit_ko"):
        defender["hp"] = 0
        messages.append(f"{attacker['name']} a mis KO {defender['name']} en un seul coup !")
        reset_temp_status(attacker)
        reset_temp_status(defender)
        return {"damage": 9999, "messages": messages}

    # 5️⃣ Si attaque inflige des dégâts
    damage = 0
    if move.get("power") or move.get("fixed_damage") or move.get("level_damage"):
        damage_info = calculate_basic_damage(attacker, defender, move)

        if isinstance(damage_info, tuple):
            damage, extra_messages = damage_info
            messages.extend(extra_messages)
        else:
            damage = damage_info

        damage = max(1, damage)
        defender["hp"] = max(0, defender.get("hp", 0) - damage)
        messages.append(f"{defender['name']} a subi {damage} dégâts !")
    else:
        messages.append(f"{attacker['name']} utilise {move['name']} sans effet direct.")

    # 6️⃣ Applique effets secondaires
    secondary_effects = apply_move_effect(attacker, defender, move, last_damage=damage)
    messages.extend(secondary_effects)

    # 🧹 Reset protections/flinch après l'action
    reset_temp_status(attacker)
    reset_temp_status(defender)

    return {"damage": damage, "messages": messages}

def calculate_basic_damage(attacker, defender, move):
    """Calcule les dégâts d'une attaque en fonction de son type."""
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
