import threading
import time
import signal
import sys

from generate_pokemon import generate_pokemon_data
from generate_types import generate_types_data
from generate_moves import generate_moves_data
from generate_items import generate_items_data
from generate_starters import generate_starters_data
from validate_data import validate_all_jsons

# === Thread-safe shutdown flag ===
shutdown_requested = False

def signal_handler(sig, frame):
    global shutdown_requested
    shutdown_requested = True
    print("\n❌ Interruption par CTRL+C. Arrêt en cours...")
    sys.exit(1)

# Bind CTRL+C
signal.signal(signal.SIGINT, signal_handler)

# Liste des tâches à lancer en thread
tasks = [
    ("Pokémon", generate_pokemon_data),
    ("Types", generate_types_data),
    ("Moves", generate_moves_data),
    ("Items", generate_items_data),
    ("Starters", generate_starters_data)
]

def run_task(name, func):
    try:
        print(f"🚀 Lancement : {name}")
        func()
        print(f"✅ Terminé : {name}")
    except Exception as e:
        print(f"❌ Erreur dans {name} : {e}")

def main():
    print("📦 Génération complète des données Pokémon Eclipse...\n")

    threads = []
    for name, func in tasks:
        t = threading.Thread(target=run_task, args=(name, func), daemon=True)
        threads.append(t)
        t.start()

    # Attente que tous les threads finissent
    for t in threads:
        while t.is_alive():
            time.sleep(0.1)

    print("\n🔎 Validation des fichiers JSON générés...")
    validate_all_jsons()
    print("\n🎉 Tous les fichiers ont été générés avec succès.")

if __name__ == "__main__":
    main()
