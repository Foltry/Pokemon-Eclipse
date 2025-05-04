# tools/evolution_patch.py

import os
import sys
import json
import requests

# Ajoute le dossier racine au path pour les imports relatifs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Chemin vers le fichier JSON à modifier
POKEMON_JSON_PATH = os.path.join("data", "pokemon.json")

def get_species_data(pokemon_id):
    """
    Récupère les données de la species du Pokémon via la PokéAPI.

    Args:
        pokemon_id (int): ID du Pokémon.

    Returns:
        dict | None: Données JSON ou None si erreur.
    """
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def get_evolution_chain(chain_url):
    """
    Récupère l'intégralité de la chaîne d'évolution.

    Args:
        chain_url (str): URL fournie par species["evolution_chain"]["url"].

    Returns:
        dict | None: Données de chaîne d’évolution ou None.
    """
    response = requests.get(chain_url)
    if response.status_code != 200:
        return None
    return response.json()

def extract_evolutions_with_levels(chain):
    """
    Convertit la chaîne d'évolution API en structure simplifiée + niveaux.

    Args:
        chain (dict): Donnée brute `chain` issue de la PokéAPI.

    Returns:
        dict: Chaîne avec champs "species", "level" (optionnel), et "evolves_to".
    """
    def recurse(node):
        evolves_to_list = []
        for evo in node.get("evolves_to", []):
            species = evo["species"]["name"]
            level = None
            details = evo.get("evolution_details", [])
            if details and "min_level" in details[0]:
                level = details[0]["min_level"]

            evo_entry = {"species": species}
            if level is not None:
                evo_entry["level"] = level
            evo_entry["evolves_to"] = recurse(evo)
            evolves_to_list.append(evo_entry)

        return evolves_to_list

    return {
        "species": chain["species"]["name"],
        "evolves_to": recurse(chain)
    }

def main():
    """
    Met à jour le fichier data/pokemon.json avec les chaînes d'évolution
    contenant les niveaux d'évolution (si disponibles).
    """
    with open(POKEMON_JSON_PATH, encoding="utf-8") as f:
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

        chain_url = species_data.get("evolution_chain", {}).get("url")
        if not chain_url:
            print(f"❌ ID {pid}: pas de chaîne trouvée")
            continue

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
