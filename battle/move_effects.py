import random

def apply_move_effect(attacker, defender, move):
    """Applique tous les effets secondaires définis dans move["effects"]"""
    effects = move.get("effects", {})
    messages = []

    # 🔥 Statut infligé
    status = effects.get("status")
    chance = effects.get("status_chance", 100)
    if status and random.randint(1, 100) <= chance:
        if not defender.get("status"):
            defender["status"] = status
            messages.append(f"{defender['name']} est maintenant {status} !")

    # 📉 Modifications de stats
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
            who = "de lui-même" if change["target"] == "user" else f"de {target['name']}"
            messages.append(f"La statistique {stat} {who} change de {sign}{delta}.")

    # 🧛 Drain
    if "drain" in effects:
        heal = int(effects["drain"] * move.get("power", 0))
        attacker["hp"] = min(attacker["hp"] + heal, attacker["stats"]["hp"])
        messages.append(f"{attacker['name']} regagne {heal} PV !")

    # 💥 Recul
    if "recoil" in effects:
        recoil = int(effects["recoil"] * move.get("power", 0))
        attacker["hp"] = max(0, attacker["hp"] - recoil)
        messages.append(f"{attacker['name']} subit {recoil} PV de recul !")

    # 🧠 Étendre : piégeage, copie, vol, statuts multiples...

    return messages
