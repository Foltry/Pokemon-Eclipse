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
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        import json
        from core.data_loader import load_json, save_json
        
        STARTER_IDS = [
            # Gen 1
            "001", "004", "007",
            # Gen 2
            "152", "155", "158",
            # Gen 3
            "252", "255", "258",
            # Gen 4
            "387", "390", "393",
            # Gen 5
            "495", "498", "501"
        ]
        
        def main():
            data = {"starters": STARTER_IDS}
            save_json("data/starters.json", data)
            print(f"✅ Fichier starters.json généré avec {len(STARTER_IDS)} starters.")
        
        if __name__ == "__main__":
            main()
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Erreur dans generate_starters.py: {e}")
        log_error("generate_starters.py", error_details)
