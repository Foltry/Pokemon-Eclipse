# tools/logger.py

import os
from datetime import datetime

# === Constantes ===
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "errors.log")


def log_error(source: str, message: str):
    """
    Enregistre un message d’erreur dans un fichier avec timestamp et source.

    Args:
        source (str): Nom du fichier ou module d’origine de l’erreur.
        message (str): Message d’erreur à enregistrer.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] [{source}] {message}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(full_message)
    except Exception as e:
        print(f"[Logger Error] Échec de l’écriture dans le log : {e}")
        print(full_message)
