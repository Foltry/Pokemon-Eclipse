# battle/move_effects.py

import random

def apply_move_effect(attacker, defender, move):
    """Applique les effets secondaires d'une attaque après avoir infligé les dégâts."""
    messages = []

    effects = move.get("effects", {})

    # 🧹 Application d'un statut
    status = effects.get("status")
    status_chance = effects.get("status_chance", 100)
    if status and random.randint(1, 100) <= status_chance:
        if not defender.get("status"):
            defender["status"] = status
            messages.append(f"{defender['name']} est maintenant {status} !")

    # 📈 Modifications de stats (boosts/débuffs)
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

    return messages
