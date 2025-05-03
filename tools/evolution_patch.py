import os
import sys
import json
import requests

# Ajout du dossier racine au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Fichier à modifier
POKEMON_JSON_PATH = os.path.join("data", "pokemon.json")

def get_species_data(pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def get_evolution_chain(chain_url):
    response = requests.get(chain_url)
    if response.status_code != 200:
        return None
    return response.json()

def extract_evolutions_with_levels(chain):
    def recurse(node):
        evolves_to_list = []
        for evo in node["evolves_to"]:
            evo_species = evo["species"]["name"]
            level = None
            evo_details = evo.get("evolution_details", [])
            if evo_details and "min_level" in evo_details[0]:
                level = evo_details[0]["min_level"]
            evo_entry = {"species": evo_species}
            if level is not None:
                evo_entry["level"] = level
            nested = recurse(evo)
            if nested:
                evo_entry["evolves_to"] = nested
            else:
                evo_entry["evolves_to"] = []
            evolves_to_list.append(evo_entry)
        return evolves_to_list

    root_species = chain["species"]["name"]
    return {
        "species": root_species,
        "evolves_to": recurse(chain)
    }

def main():
    with open(POKEMON_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("🔍 Récupération des évolutions via PokéAPI...")
    modified = 0

    for entry in data:
        pid = entry.get("id")
        if not pid:
            continue

        species_data = get_species_data(pid)
        if not species_data:
            print(f"❌ ID {pid}: erreur API species")
            continue

        chain_url = species_data["evolution_chain"]["url"]
        evo_chain = get_evolution_chain(chain_url)
        if not evo_chain:
            print(f"❌ ID {pid}: erreur API chain")
            continue

        chain_data = extract_evolutions_with_levels(evo_chain["chain"])
        entry["evolution"] = chain_data
        print(f"✅ ID {pid} : évolutions mises à jour")
        modified += 1

    with open(POKEMON_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Patch terminé : {modified} Pokémon mis à jour avec les niveaux d’évolution.")

if __name__ == "__main__":
    main()
