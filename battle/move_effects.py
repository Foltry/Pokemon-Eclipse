import random

def apply_move_effect(attacker, defender, move, last_damage=0):
    """Applique les effets secondaires d'une attaque après avoir infligé les dégâts."""
    messages = []
    effects = move.get("effects", {})

    status = effects.get("status")
    status_chance = effects.get("status_chance", 100)
    if status and random.randint(1, 100) <= status_chance:
        if not defender.get("status"):
            defender["status"] = status
            messages.append(f"{defender['name']} est maintenant {status} !")

    stat_changes = effects.get("stat_changes", [])
    for change in stat_changes:
        if random.randint(1, 100) <= change.get("chance", 100):
            target = attacker if change["target"] == "user" else defender
            stat = change["stat"]
            delta = change["change"]

            if "boosts" not in target:
                target["boosts"] = {}
            target["boosts"][stat] = target["boosts"].get(stat, 0) + delta

            sign = "+" if delta > 0 else ""
            who = "lui-même" if change["target"] == "user" else target["name"]
            messages.append(f"La statistique {stat} de {who} change de {sign}{delta}.")

    if effects.get("protect"):
        attacker["_protected"] = True
        messages.append(f"{attacker['name']} se protège contre les attaques !")

    if effects.get("recharge"):
        attacker["_recharging"] = True
        messages.append(f"{attacker['name']} devra recharger au prochain tour !")

    flinch_chance = effects.get("flinch_chance")
    if flinch_chance and random.randint(1, 100) <= flinch_chance:
        defender["_flinched"] = True
        messages.append(f"{defender['name']} a eu peur et pourrait ne pas agir !")

    drain_percent = effects.get("drain_percent")
    if drain_percent and last_damage > 0:
        heal = int(last_damage * drain_percent / 100)
        max_hp = attacker.get("stats", {}).get("hp", 1)
        attacker["hp"] = min(attacker.get("hp", 0) + heal, max_hp)
        messages.append(f"{attacker['name']} récupère {heal} PV grâce à {move['name']} !")

    recoil_percent = effects.get("recoil_percent")
    if recoil_percent and last_damage > 0:
        recoil = int(last_damage * recoil_percent / 100)
        attacker["hp"] = max(0, attacker.get("hp", 0) - recoil)
        messages.append(f"{attacker['name']} subit {recoil} dégâts de recul !")

    new_weather = effects.get("weather")
    if new_weather:
        messages.append(f"Le climat change : {new_weather.capitalize()} !")

    return messages
