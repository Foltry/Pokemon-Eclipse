import os, json, requests
from tqdm import tqdm

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(BASE, "data")
SPRITES = os.path.join(BASE, "assets", "sprites", "pokemon")
os.makedirs(DATA, exist_ok=True)

SPRITE_TYPES = [
    "front_default", "back_default", "front_shiny", "back_shiny",
    "front_female", "back_female", "front_shiny_female", "back_shiny_female"
]

def download_sprite(url, path):
    if url and not os.path.exists(path):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
        except:
            pass

def generate_pokemon_data():
    pokemons = {}
    for t in SPRITE_TYPES:
        os.makedirs(os.path.join(SPRITES, t.replace("default", "front")), exist_ok=True)

    for i in tqdm(range(1, 650), desc="📥 Pokémon"):
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}")
        if res.status_code != 200:
            continue
        d = res.json()

        # Nom en français (fallback : nom par défaut)
        name = d["name"]
        species_data = requests.get(d["species"]["url"]).json()
        name_fr = next((n["name"] for n in species_data["names"] if n["language"]["name"] == "fr"), name)

        poke_id = str(i).zfill(3)
        pokemons[poke_id] = {
            "name": name_fr,
            "types": [t["type"]["name"].capitalize() for t in d["types"]],
            "base_hp": next(s["base_stat"] for s in d["stats"] if s["stat"]["name"] == "hp"),
            "base_attack": next(s["base_stat"] for s in d["stats"] if s["stat"]["name"] == "attack"),
            "base_defense": next(s["base_stat"] for s in d["stats"] if s["stat"]["name"] == "defense"),
            "moves": [m["move"]["name"] for m in d["moves"][:4]]
        }

        sprites = d["sprites"]["versions"]["generation-v"]["black-white"]["animated"]
        for t in SPRITE_TYPES:
            sprite_url = sprites.get(t)
            if sprite_url:
                folder = t.replace("default", "front")
                save_path = os.path.join(SPRITES, folder, f"{poke_id}.gif")
                download_sprite(sprite_url, save_path)

    with open(os.path.join(DATA, "pokemon.json"), "w", encoding="utf-8") as f:
        json.dump(pokemons, f, indent=2)
