# tools/generate_sprites.py

import os
import json
import requests
from logger import log_error

# === Constantes ===
SPRITE_DIR = os.path.join("assets", "sprites", "pokemon")
POKEMON_DATA_PATH = os.path.join("data", "pokemon.json")
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown"


def parse_filename_to_url(filename):
    """
    Construit l’URL complète du sprite en fonction de son nom de fichier.

    Exemple : "001_front_shiny_female.gif" → URL vers shiny/female/back/001.gif

    Args:
        filename (str): Nom du fichier GIF local.

    Returns:
        str: URL complète vers le sprite distant.
    """
    parts = filename.replace(".gif", "").split("_")
    poke_id = str(int(parts[0]))  # Convertit "001" → "1"
    path_parts = []

    if "female" in parts:
        path_parts.append("female")
    if "shiny" in parts:
        path_parts.append("shiny")
    if "back" in parts:
        path_parts.append("back")

    path = "/".join(path_parts)
    return f"{SPRITE_BASE_URL}/" + (f"{path}/" if path else "") + f"{poke_id}.gif"


def download_sprite(filename):
    """
    Télécharge un sprite animé si non présent localement.

    Args:
        filename (str): Nom de fichier GIF (ex: "001_front.gif")
    """
    try:
        url = parse_filename_to_url(filename)
        local_path = os.path.join(SPRITE_DIR, filename)

        if not os.path.exists(local_path):
            response = requests.get(url)
            if response.status_code == 200:
                os.makedirs(SPRITE_DIR, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ {filename} téléchargé")
            else:
                print(f"⚠️ {filename} introuvable (HTTP {response.status_code})")
                log_error("generate_sprites.py", f"Sprite manquant : {url}")
        else:
            print(f"✔️  {filename} déjà présent")
    except Exception as e:
        log_error("generate_sprites.py", f"Erreur téléchargement {filename} : {e}")


def main():
    """
    Charge tous les noms de sprites présents dans `pokemon.json`,
    puis télécharge ceux qui manquent dans le dossier `assets/sprites/pokemon/`.
    """
    if not os.path.exists(POKEMON_DATA_PATH):
        print("❌ Fichier pokemon.json introuvable.")
        return

    with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
        pokemon_data = json.load(f)

    all_sprites = {
        filename
        for poke in pokemon_data
        for filename in poke.get("sprites", {}).values()
        if filename
    }

    print(f"🎮 Téléchargement de {len(all_sprites)} sprites animés...\n")
    for filename in sorted(all_sprites):
        download_sprite(filename)

    print("\n✅ Téléchargement terminé.")


if __name__ == "__main__":
    main()
