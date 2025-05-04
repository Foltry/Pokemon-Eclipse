# tools/patch_moves.py

import sys
import os
import json
import requests
from tqdm import tqdm

# Ajout du dossier racine au path pour imports éventuels
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === Constantes ===
MOVES_PATH = os.path.join("data", "moves.json")
POKEAPI_MOVE_URL = "https://pokeapi.co/api/v2/move"

# Mapping PokéAPI → format projet
STAT_MAP = {
    "attack": "atk",
    "defense": "def",
    "special-attack": "spa",
    "special-defense": "spd",
    "speed": "spe",
    "accuracy": "acc",
    "evasion": "eva",
    "hp": "hp"
}

# === Chargement des attaques existantes ===
with open(MOVES_PATH, "r", encoding="utf-8") as f:
    moves = json.load(f)

patched_count = 0

# === Traitement de chaque attaque ===
for move in tqdm(moves, desc="🔄 Mise à jour des effets secondaires"):
    name_en = move.get("name_en", "").lower()
    if not name_en:
        continue

    try:
        response = requests.get(f"{POKEAPI_MOVE_URL}/{name_en}")
        if response.status_code != 200:
            continue
        data = response.json()

        effect = {}

        # Ajout des changements de stats
        stat_changes = data.get("stat_changes", [])
        if stat_changes:
            effect["stat_changes"] = []
            for change in stat_changes:
                stat_name = change["stat"]["name"]
                effect["stat_changes"].append({
                    "stat": STAT_MAP.get(stat_name, stat_name[:3]),
                    "change": change["change"],
                    "target": "opponent",
                    "chance": 100
                })

        # Ajout du texte d'effet (FR)
        for entry in data.get("effect_entries", []):
            if entry["language"]["name"] == "fr":
                effect["text"] = entry.get("short_effect", "").strip()
                break

        # Attaques spéciales de type "protect"
        if name_en in ["protect", "detect", "spiky-shield"]:
            effect["protect"] = True

        if effect:
            move["effects"] = effect
            patched_count += 1

    except Exception as e:
        print(f"❌ Erreur lors du traitement de {name_en} : {e}")

# === Sauvegarde du fichier mis à jour ===
with open(MOVES_PATH, "w", encoding="utf-8") as f:
    json.dump(moves, f, ensure_ascii=False, indent=2)

print(f"\n✅ {patched_count} attaques mises à jour avec effets dans moves.json")
