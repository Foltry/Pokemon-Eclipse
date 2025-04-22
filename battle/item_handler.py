import os
import json
from battle.capture_handler import attempt_capture

# Charge les données d'objets
with open(os.path.join("data", "items.json"), encoding="utf-8") as f:
    ITEM_DATA = {item["name"]: item for item in json.load(f)}

# Liste d’objets utilisables uniquement hors combat
NON_BATTLE_ITEMS = [
    "Rappel Max", "Rappel", "Repousse", "Super Bonbon"
]

def can_use_item_in_battle(item_name):
    """Vérifie si l’objet est utilisable en combat."""
    return item_name in ITEM_DATA and item_name not in NON_BATTLE_ITEMS

def use_item_on_pokemon(item_name, target):
    """Applique les effets de l’objet sur un Pokémon (en combat)."""
    result = {
        "success": False,
        "messages": [],
    }

    item = ITEM_DATA.get(item_name)
    if not item:
        result["messages"].append(f"L’objet {item_name} est inconnu.")
        return result

    if not can_use_item_in_battle(item_name):
        result["messages"].append(f"Impossible d’utiliser {item_name} pendant un combat.")
        return result

    # Tentative de capture si c’est une Poké Ball
    if item.get("category") == "standard-balls":
        success, messages = attempt_capture(target, item_name, target.get("status"))
        result["success"] = success
        result["messages"].extend(messages)
        return result

    # Soin de PV
    if "healing" in item:
        heal_amount = item["healing"]
        if target["stats"]["hp"] <= 0:
            result["messages"].append(f"{target['name']} est KO. Impossible d’utiliser {item_name}.")
            return result
        if target["stats"]["hp"] == target["stats"]["max_hp"]:
            result["messages"].append(f"{target['name']} a déjà tous ses PV.")
            return result
        healed = min(heal_amount, target["stats"]["max_hp"] - target["stats"]["hp"])
        target["stats"]["hp"] += healed
        result["success"] = True
        result["messages"].append(f"{item_name} a restauré {healed} PV à {target['name']}.")

    # Guérison de statut
    elif "status_heal" in item:
        if not target.get("status"):
            result["messages"].append(f"{target['name']} n’a aucun problème de statut.")
            return result
        if item["status_heal"] == "all" or target["status"] in item["status_heal"]:
            result["success"] = True
            result["messages"].append(f"{target['name']} n’est plus {target['status']} !")
            target["status"] = None
        else:
            result["messages"].append(f"{item_name} ne peut pas soigner ce statut.")
            return result

    else:
        result["messages"].append(f"{item_name} n’a aucun effet en combat.")
        return result

    return result
