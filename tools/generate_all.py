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
        import sys
        import threading
        import subprocess
        from pathlib import Path
        
        # ✅ Utilise l'interpréteur Python actuel (celui de la venv)
        PYTHON_EXEC = sys.executable
        
        SCRIPTS = [
            "generate_pokemon.py",
            "generate_moves.py",
            "generate_items.py",
            "generate_types.py",
            "generate_starters.py"
        ]
        
        def run_script(script):
            name = os.path.basename(script)
            print(f"🚀 Lancement : {name}")
            try:
                subprocess.run([PYTHON_EXEC, script], check=True)
                print(f"✅ Terminé : {name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur dans {name}: {e}")
        
        def main():
            base_path = Path(__file__).parent
            threads = []
        
            for script_name in SCRIPTS:
                script_path = str(base_path / script_name)
                thread = threading.Thread(target=run_script, args=(script_path,))
                thread.start()
                threads.append(thread)
        
            for thread in threads:
                thread.join()
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_all.py: {e}")
        log_error("generate_all.py", error_details)
