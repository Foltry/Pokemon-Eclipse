# battle/item_handler.py

from data.items_loader import get_item_data
from battle.capture_handler import attempt_capture

# Liste des objets non utilisables en combat
NON_BATTLE_ITEMS = [
    "Rappel Max", "Rappel", "Repousse", "Super Bonbon"
]

def can_use_item_in_battle(item_name):
    """Vérifie si l’objet est utilisable en combat."""
    item = get_item_data(item_name)
    return item is not None and item_name not in NON_BATTLE_ITEMS

def use_item_on_pokemon(item_name, target):
    """
    Applique les effets de l’objet sur un Pokémon (en combat).
    Peut être une Poké Ball, un soin de PV ou un soin de statut.
    Retourne un dictionnaire : {success: bool, messages: list[str], ...}
    """
    item = get_item_data(item_name)
    if not item:
        return {
            "success": False,
            "messages": [f"L’objet {item_name} est inconnu."]
        }

    if not can_use_item_in_battle(item_name):
        return {
            "success": False,
            "messages": [f"Impossible d’utiliser {item_name} pendant un combat."]
        }

    # === Poké Balls ===
    if item.get("category") == "standard-balls":
        return attempt_capture(target, item_name, target.get("status"))

    # === Soins de PV ===
    if "healing" in item:
        current_hp = target["stats"]["hp"]
        max_hp = target["stats"].get("max_hp", current_hp)

        if current_hp <= 0:
            return {
                "success": False,
                "messages": [f"{target['name']} est KO. Impossible d’utiliser {item_name}."]
            }
        if current_hp == max_hp:
            return {
                "success": False,
                "messages": [f"{target['name']} a déjà tous ses PV."]
            }

        heal_amount = item["healing"]
        healed = min(heal_amount, max_hp - current_hp)
        target["stats"]["hp"] += healed

        return {
            "success": True,
            "messages": [f"{item_name} a restauré {healed} PV à {target['name']}."]
        }

    # === Soins de statut ===
    if "status_heal" in item:
        current_status = target.get("status")
        if not current_status:
            return {
                "success": False,
                "messages": [f"{target['name']} n’a aucun problème de statut."]
            }

        status_heal = item["status_heal"]
        if status_heal == "all" or current_status in status_heal:
            target["status"] = None
            return {
                "success": True,
                "messages": [f"{target['name']} n’est plus {current_status} !"]
            }
        else:
            return {
                "success": False,
                "messages": [f"{item_name} ne peut pas soigner ce statut."]
            }

    # === Par défaut : aucun effet connu ===
    return {
        "success": False,
        "messages": [f"{item_name} n’a aucun effet en combat."]
    }
