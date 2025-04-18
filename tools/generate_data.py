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
        import argparse
        import subprocess
        
        SCRIPTS = {
            "items": "tools/generate_items.py",
            "moves": "tools/generate_moves.py",
            "pokemon": "tools/generate_pokemon.py",
            "types": "tools/generate_types.py",
            "starters": "tools/generate_starters.py",
        }
        
        def run_script(path, verbose=False):
            cmd = ["python", path]
            if verbose:
                cmd.append("--verbose")
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de l’exécution de {path}: {e}")
        
        def main():
            parser = argparse.ArgumentParser(description="Générer les données du jeu.")
            parser.add_argument("--all", action="store_true", help="Tout générer.")
            parser.add_argument("--verbose", action="store_true", help="Mode verbeux.")
            for name in SCRIPTS:
                parser.add_argument(f"--{name}", action="store_true", help=f"Générer uniquement {name}.")
            args = parser.parse_args()
        
            to_run = [name for name in SCRIPTS if getattr(args, name)]
            if args.all or not to_run:
                to_run = list(SCRIPTS.keys())
        
            for name in to_run:
                print(f"➡️ Génération : {name}")
                run_script(SCRIPTS[name], verbose=args.verbose)
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_data.py: {e}")
        log_error("generate_data.py", error_details)
