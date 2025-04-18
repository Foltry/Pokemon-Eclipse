import json, os

files = {
    "pokemon": "data/pokemon.json",
    "items": "data/items.json",
    "moves": "data/moves.json",
    "types": "data/types.json",
    "starters": "data/starters.json"
}

for name, path in files.items():
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ {name} : OK ({len(data)} entrées)")
    except Exception as e:
        print(f"❌ {name} : erreur ({e})")