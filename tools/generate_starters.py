import os, json, random, argparse

POKE_PATH = "data/pokemon.json"
STARTER_PATH = "data/starters.json"

def load(path):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f: return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def by_type(data):
    types = {"fire": [], "water": [], "grass": []}
    for pid, poke in data.items():
        for t in poke.get("types", []):
            if t in types:
                types[t].append(pid)
                break
    if not all(types.values()): return []
    return random.sample(types["fire"], 1) + random.sample(types["water"], 1) + random.sample(types["grass"], 1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--by-type", action="store_true")
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    pokemon = load(POKE_PATH)
    ids = list(pokemon.keys())
    if len(ids) < 3:
        print("❌ Moins de 3 Pokémon.")
        return

    starters = by_type(pokemon) if args.by_type else random.sample(ids, 3)
    if args.shuffle: random.shuffle(starters)
    if args.verbose: print("⭐ Starters :", starters)

    save(STARTER_PATH, starters)
    print("✅ starters.json mis à jour.")

if __name__ == "__main__":
    main()