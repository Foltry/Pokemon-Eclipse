# tools/correct_pokemon.py

import json
import requests
import os

POKEMON_JSON_PATH = os.path.join("data", "pokemon.json")

# Charger le JSON existant
with open(POKEMON_JSON_PATH, encoding="utf-8") as f:
    pokemon_data = json.load(f)

# Télécharger les noms français
print("🔎 Téléchargement des noms français de toutes les espèces...")
species_url = "https://pokeapi.co/api/v2/pokemon-species?limit=10000"
species_data = requests.get(species_url).json()["results"]

# Construction du dictionnaire de traduction EN → FR
name_translation = {}
for species in species_data:
    species_detail = requests.get(species["url"]).json()
    for name in species_detail.get("names", []):
        if name["language"]["name"] == "fr":
            name_translation[species_detail["name"]] = name["name"]
            break

print(f"✅ {len(name_translation)} traductions récupérées.")

# Cache des noms de capacités françaises
move_translation = {}

def get_french_move_name(move_name_en):
    """
    Récupère le nom français d'une attaque à partir de son nom anglais.

    Args:
        move_name_en (str): Nom anglais de la capacité.

    Returns:
        str: Nom français si trouvé, sinon nom original.
    """
    if move_name_en in move_translation:
        return move_translation[move_name_en]

    move_url = f"https://pokeapi.co/api/v2/move/{move_name_en}"
    response = requests.get(move_url)
    if response.status_code != 200:
        return move_name_en

    move_data = response.json()
    for name in move_data.get("names", []):
        if name["language"]["name"] == "fr":
            move_translation[move_name_en] = name["name"]
            return name["name"]
    return move_name_en

def get_level_up_moves(pokemon_name_en):
    """
    Récupère les attaques apprises par montée de niveau pour un Pokémon donné.

    Args:
        pokemon_name_en (str): Nom anglais du Pokémon.

    Returns:
        list[dict]: Liste de mouvements avec leur niveau d'apprentissage.
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name_en.lower()}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Impossible de récupérer {pokemon_name_en}")
        return []

    moves = []
    for move_entry in response.json().get("moves", []):
        for version_detail in move_entry.get("version_group_details", []):
            if version_detail["move_learn_method"]["name"] == "level-up":
                level = version_detail["level_learned_at"]
                if level > 0:
                    move_name = get_french_move_name(move_entry["move"]["name"])
                    moves.append({"name": move_name, "level": level})

    # Supprimer les doublons
    unique_moves = { (m["name"], m["level"]): m for m in moves }
    return list(unique_moves.values())

def correct_chain(chain):
    """
    Applique les traductions sur une chaîne d’évolution récursive.

    Args:
        chain (dict): Structure de la chaîne d’évolution.
    """
    if "species" in chain and chain["species"] in name_translation:
        chain["species"] = name_translation[chain["species"]]
    for evo in chain.get("evolves_to", []):
        correct_chain(evo)

# Correction des données
print("🚀 Correction du fichier...")

for poke in pokemon_data:
    species_en = poke["evolution"]["species"].lower()
    correct_chain(poke["evolution"])
    poke["moves"] = sorted(get_level_up_moves(species_en), key=lambda m: m["level"])

print("✅ Correction terminée.")

# Sauvegarde dans le fichier
with open(POKEMON_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(pokemon_data, f, ensure_ascii=False, indent=2)

print("💾 Nouveau fichier sauvegardé dans data/pokemon.json.")
