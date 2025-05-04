import sys
import os
import json
import requests
from tqdm import tqdm

# 📁 Corriger le chemin d'accès depuis ./tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🔄 Charger moves.json original
moves_path = os.path.join("data", "moves.json")
with open(moves_path, "r", encoding="utf-8") as f:
    moves = json.load(f)

# 🧠 Mapping stats PokéAPI → ton format projet
stat_map = {
    "attack": "atk",
    "defense": "def",
    "special-attack": "spa",
    "special-defense": "spd",
    "speed": "spe",
    "accuracy": "acc",
    "evasion": "eva",
    "hp": "hp"
}

patched_count = 0
for move in tqdm(moves, desc="🔄 Mise à jour"):
    name_en = move.get("name_en", "").lower()
    if not name_en:
        continue

    try:
        url = f"https://pokeapi.co/api/v2/move/{name_en}"
        res = requests.get(url)
        if res.status_code != 200:
            continue

        data = res.json()
        effect = {}

        # 📉 Ajout des effets de stat
        stat_changes = data.get("stat_changes", [])
        if stat_changes:
            effect["stat_changes"] = []
            for s in stat_changes:
                raw_stat = s["stat"]["name"]
                effect["stat_changes"].append({
                    "stat": stat_map.get(raw_stat, raw_stat[:3]),
                    "change": s["change"],
                    "target": "opponent",
                    "chance": 100
                })

        # 💬 Ajout du texte de l’effet en français
        for entry in data.get("effect_entries", []):
            if entry["language"]["name"] == "fr":
                effect["text"] = entry.get("short_effect", "").strip()
                break

        # 🛡️ Cas spécial : attaque de protection
        if name_en in ["protect", "detect", "spiky-shield"]:
            effect["protect"] = True

        if effect:
            move["effects"] = effect
            patched_count += 1

    except Exception as e:
        print(f"❌ Erreur avec {name_en} : {e}")

# 💾 Écriture DIRECTE dans moves.json
with open(moves_path, "w", encoding="utf-8") as f:
    json.dump(moves, f, ensure_ascii=False, indent=2)

print(f"\n✅ {patched_count} attaques mises à jour dans moves.json")
