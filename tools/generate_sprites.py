import os
import json
import requests
from logger import log_error

SPRITE_DIR = os.path.join("assets", "sprites", "pokemon")
POKEMON_DATA_PATH = os.path.join("data", "pokemon.json")
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown"

def parse_filename_to_url(filename):
    # Ex: "001_front_shiny_female.gif" → ["001", "front", "shiny", "female"]
    parts = filename.replace(".gif", "").split("_")
    poke_id = str(int(parts[0]))  # Enlève les zéros inutiles
    path = []

    if "shiny" in parts:
        path.append("shiny")
    if "back" in parts:
        path.append("back")
    if "female" in parts:
        path.insert(0, "female")  # Important : female peut précéder shiny

    sub_path = "/".join(path)
    url = f"{SPRITE_BASE_URL}/" + (f"{sub_path}/" if sub_path else "") + f"{poke_id}.gif"
    return url

def download_sprite(filename):
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
        log_error("generate_sprites.py", f"Erreur download {filename} : {e}")

def main():
    if not os.path.exists(POKEMON_DATA_PATH):
        print("❌ Fichier pokemon.json introuvable.")
        return

    with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
        pokemon_data = json.load(f)

    all_sprites = set()

    for p in pokemon_data:
        for variant, filename in p.get("sprites", {}).items():
            if filename:
                all_sprites.add(filename)

    print(f"🎮 Téléchargement de {len(all_sprites)} sprites animés...\n")
    for filename in sorted(all_sprites):
        download_sprite(filename)

    print("\n✅ Téléchargement terminé.")

if __name__ == "__main__":
    main()
