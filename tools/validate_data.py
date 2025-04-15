import os, json

def validate_all_jsons():
    print("🔍 Validation des fichiers JSON...")
    for file in ["pokemon.json", "types.json", "moves.json", "items.json", "starters.json"]:
        try:
            with open(os.path.join("../data", file), encoding='utf-8') as f:
                json.load(f)
        except Exception as e:
            print(f"❌ Erreur dans {file} : {e}")
            return
    print("✅ Tous les fichiers JSON sont valides.")
