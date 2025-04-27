import json
import requests
import os

# Charger le JSON existant
POKEMON_JSON_PATH = os.path.join("data", "pokemon.json")

with open(POKEMON_JSON_PATH, encoding="utf-8") as f:
    pokemon_data = json.load(f)

# Préparer un mapping EN->FR des noms de Pokémon
print("🔎 Téléchargement des noms français de toutes les espèces...")
species_url = "https://pokeapi.co/api/v2/pokemon-species?limit=10000"
species_data = requests.get(species_url).json()["results"]

name_translation = {}
for species in species_data:
    species_detail = requests.get(species["url"]).json()
    fr_name = None
    for name in species_detail["names"]:
        if name["language"]["name"] == "fr":
            fr_name = name["name"]
            break
    if fr_name:
        name_translation[species_detail["name"]] = fr_name

print(f"✅ {len(name_translation)} traductions récupérées.")

# Préparer un cache de moves français
move_translation = {}

def get_french_move_name(move_name_en):
    """Récupère le nom français d'une attaque."""
    if move_name_en in move_translation:
        return move_translation[move_name_en]

    move_url = f"https://pokeapi.co/api/v2/move/{move_name_en}"
    response = requests.get(move_url)
    if response.status_code != 200:
        return move_name_en

    move_data = response.json()
    for name in move_data["names"]:
        if name["language"]["name"] == "fr":
            move_translation[move_name_en] = name["name"]
            return name["name"]
    return move_name_en

# Fonction pour extraire les moves d'un Pokémon
def get_level_up_moves(pokemon_name_en):
    """Retourne les attaques apprises par montée de niveau pour un Pokémon donné."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name_en.lower()}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Impossible de récupérer {pokemon_name_en}")
        return []

    data = response.json()
    moves = []
    for move_entry in data["moves"]:
        for version_detail in move_entry["version_group_details"]:
            if version_detail["move_learn_method"]["name"] == "level-up":
                move_fr = get_french_move_name(move_entry["move"]["name"])
                level_learned = version_detail["level_learned_at"]
                if level_learned > 0:
                    moves.append({
                        "name": move_fr,
                        "level": level_learned
                    })
    # Éviter les doublons exacts
    unique_moves = { (m["name"], m["level"]) : m for m in moves }
    return list(unique_moves.values())

# Correction complète du fichier
print("🚀 Correction du fichier...")

for poke in pokemon_data:
    poke_species = poke["evolution"]["species"].lower()
    
    # Corriger les chaînes d'évolution
    def correct_chain(chain):
        if "species" in chain and chain["species"] in name_translation:
            chain["species"] = name_translation[chain["species"]]
        if "evolves_to" in chain:
            for evo in chain["evolves_to"]:
                correct_chain(evo)
    
    correct_chain(poke["evolution"])

    # Récupérer moves
    en_name = poke_species
    moves = get_level_up_moves(en_name)
    poke["moves"] = sorted(moves, key=lambda m: m["level"])

print("✅ Correction terminée.")

# Réécrire proprement
with open(POKEMON_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(pokemon_data, f, ensure_ascii=False, indent=2)

print("💾 Nouveau fichier sauvegardé dans data/pokemon.json.")
