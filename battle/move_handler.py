from battle.engine import calculate_damage
from battle.move_effects import apply_move_effect
from battle.move_utils import (
    check_accuracy,
    is_protected,
    should_fail,
    process_multi_hit,
    get_fixed_damage,
)
import random

def use_move(attacker, defender, move, last_move=None):
    result = {
        "move_name": move["name"],
        "attacker": attacker["name"],
        "messages": [],
    }

    # 1. Cas d’échec automatique
    if should_fail(attacker, defender, move, last_move):
        result["messages"].append(f"{attacker['name']} utilise {move['name']}...")
        result["messages"].append("Mais cela échoue !")
        return result

    # 2. Abri ?
    if is_protected(defender):
        result["messages"].append(f"{attacker['name']} utilise {move['name']}...")
        result["messages"].append(f"{defender['name']} se protège avec Abri !")
        return result

    result["messages"].append(f"{attacker['name']} utilise {move['name']} !")

    # 3. Attaque à chargement
    if move.get("charge_turn") and not attacker.get("_charging"):
        attacker["_charging"] = move
        result["messages"].append(f"{attacker['name']} commence à charger {move['name']}...")
        return result
    elif "_charging" in attacker:
        del attacker["_charging"]

    # 4. Précision
    if not check_accuracy(attacker, defender, move):
        result["messages"].append("L’attaque échoue !")
        return result

    # 5. OHKO ?
    if move.get("one_hit_ko"):
        if attacker["level"] < defender["level"]:
            result["messages"].append("Cela ne marche pas sur un niveau supérieur !")
            return result
        if random.random() <= move.get("accuracy", 30) / 100:
            defender["hp"] = 0
            result["messages"].append("Coup KO immédiat !")
        else:
            result["messages"].append("L’attaque rate !")
        return result

    # 6. Dégâts fixes
    if move.get("fixed_damage"):
        damage = get_fixed_damage(attacker, move)
        defender["hp"] = max(0, defender["hp"] - damage)
        result["messages"].append(f"{defender['name']} perd {damage} PV.")
        return result

    # 7. Attaque multi-coups
    if move.get("multi_hit"):
        hits, total_dmg, any_crit, eff = process_multi_hit(attacker, defender, move)
        defender["hp"] = max(0, defender["hp"] - total_dmg)
        result["messages"].append(f"L’attaque frappe {hits} fois !")
        if any_crit:
            result["messages"].append("Coup critique !")
        if eff > 1:
            result["messages"].append("C’est super efficace !")
        elif eff < 1 and eff > 0:
            result["messages"].append("Ce n’est pas très efficace...")
        elif eff == 0:
            result["messages"].append("Ça n’a aucun effet...")
        result["messages"].append(f"{defender['name']} perd {total_dmg} PV.")
    else:
        # 8. Attaque standard
        dmg, is_crit, mult = calculate_damage(attacker, defender, move)
        defender["hp"] = max(0, defender["hp"] - dmg)

        if is_crit:
            result["messages"].append("Coup critique !")
        if mult > 1:
            result["messages"].append("C’est super efficace !")
        elif mult < 1 and mult > 0:
            result["messages"].append("Ce n’est pas très efficace...")
        elif mult == 0:
            result["messages"].append("Ça n’a aucun effet...")

        result["messages"].append(f"{defender['name']} perd {dmg} PV.")

    # 9. Recharge
    if move.get("recharge_turn"):
        attacker["_recharging"] = True

    # 10. Effets secondaires
    if defender["hp"] > 0:
        result["messages"] += apply_move_effect(attacker, defender, move)

    return result
