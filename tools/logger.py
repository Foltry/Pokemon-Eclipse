# tools/logger.py

import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "errors.log")

def log_error(source: str, message: str):
    """
    Log an error message with timestamp and source script.

    Args:
        source (str): Nom du fichier ou module où l’erreur a eu lieu.
        message (str): Message d’erreur à logguer.
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] [{source}] {message}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(full_message)
    except Exception as e:
        print(f"[Logger Error] Impossible d’écrire dans le fichier log : {e}")
        print(full_message)
