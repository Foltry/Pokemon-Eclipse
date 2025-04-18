import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
LOG_PATH = os.path.join("tools", "logs")
os.makedirs(LOG_PATH, exist_ok=True)
ERROR_LOG_FILE = os.path.join(LOG_PATH, "generation_errors.log")

def log_error(script_name, error_text):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"--- Erreur dans {script_name} ---\n")
        log_file.write(error_text + "\n\n")

if __name__ == "__main__":
    try:
        import os
        import json
        import argparse
        
        REQUIRED = {
            "pokemon": {"name", "types", "base_hp", "base_attack", "base_defense", "moves", "base_experience"},
            "items": {"name", "category", "effect", "sprite"},
            "moves": {"name", "power", "pp", "type", "accuracy"},
            "types": {"name", "damage_relations"},
        }
        
        SPRITES_DIR = {
            "front": "assets/sprites/pokemon/front",
            "back": "assets/sprites/pokemon/back"
        }
        
        def load_json(path):
            if not os.path.exists(path):
                print(f"❌ Fichier manquant : {path}")
                return {}
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        
        def validate_entries(data, required_keys, verbose=False):
            errors = []
            for k, entry in data.items():
                missing = [key for key in required_keys if key not in entry]
                if missing:
                    errors.append((k, missing))
                    if verbose:
                        print(f"[!] {k} : clés manquantes -> {missing}")
            return errors
        
        def validate_sprites(pokemon_ids, verbose=False):
            missing = []
            for pid in pokemon_ids:
                for side in ["front", "back"]:
                    path = os.path.join(SPRITES_DIR[side], f"{pid}.gif")
                    if not os.path.exists(path):
                        missing.append((pid, side))
                        if verbose:
                            print(f"[SPRITE] Manquant : {side}/{pid}.gif")
            return missing
        
        def main():
            parser = argparse.ArgumentParser()
            parser.add_argument("--verbose", action="store_true", help="Afficher les détails")
            args = parser.parse_args()
        
            all_ok = True
        
            # Validation Pokémon
            pokedata = load_json("data/pokemon.json")
            errors = validate_entries(pokedata, REQUIRED["pokemon"], args.verbose)
            if errors:
                print(f"❌ Pokémon incomplets : {len(errors)}")
                all_ok = False
        
            # Sprites
            missing_sprites = validate_sprites(pokedata.keys(), args.verbose)
            if missing_sprites:
                print(f"❌ Sprites manquants : {len(missing_sprites)}")
                all_ok = False
        
            # Validation objets
            itemdata = load_json("data/items.json")
            errors = validate_entries(itemdata, REQUIRED["items"], args.verbose)
            if errors:
                print(f"❌ Objets incomplets : {len(errors)}")
                all_ok = False
        
            # Validation attaques
            movedata = load_json("data/moves.json")
            errors = validate_entries(movedata, REQUIRED["moves"], args.verbose)
            if errors:
                print(f"❌ Attaques incomplètes : {len(errors)}")
                all_ok = False
        
            # Validation types
            typedata = load_json("data/types.json")
            errors = validate_entries(typedata, REQUIRED["types"], args.verbose)
            if errors:
                print(f"❌ Types incomplets : {len(errors)}")
                all_ok = False
        
            # Validation starters
            starters = load_json("data/starters.json")
            if not isinstance(starters, list) or not all(str(p) in pokedata for p in starters):
                print("❌ Fichier starters.json invalide ou contient des IDs inconnus")
                all_ok = False
            elif args.verbose:
                print(f"✅ Starters valides : {starters}")
        
            if all_ok:
                print("✅ Tous les fichiers sont valides !")
            else:
                print("⚠️ Des erreurs ont été détectées.")
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans validate_data.py: {e}")
        log_error("validate_data.py", error_details)
