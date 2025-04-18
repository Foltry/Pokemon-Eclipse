import threading
import subprocess
import os
import sys

SCRIPTS = [
    "generate_pokemon.py",
    "generate_moves.py",
    "generate_items.py",
    "generate_types.py",
    "generate_starters.py"
]

SCRIPT_PATHS = [os.path.join("tools", script) for script in SCRIPTS]

def run_script(path):
    try:
        print(f"🚀 Lancement : {os.path.basename(path)}")
        subprocess.run([sys.executable, path], check=True)
        print(f"✅ Terminé : {os.path.basename(path)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur dans {path}: {e}")

def main():
    threads = []
    for path in SCRIPT_PATHS:
        thread = threading.Thread(target=run_script, args=(path,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("\n✅ Tous les scripts ont été exécutés.")

if __name__ == "__main__":
    main()
