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
