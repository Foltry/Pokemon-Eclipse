import random
from data.pokemon_loader import get_all_pokemon

def get_balanced_enemy(ally_pokemon, level_margin=1, stat_margin=0.15):
    all_pokemon = get_all_pokemon()
    
    ally_level = ally_pokemon.get("level", 5)
    ally_base_stats = ally_pokemon.get("base_stats", {})
    ally_total_stats = sum(ally_base_stats.values())

    level_range = range(max(1, ally_level - level_margin), ally_level + level_margin + 1)
    stat_min = int(ally_total_stats * (1.0 - stat_margin))
    stat_max = int(ally_total_stats * (1.0 + stat_margin))

    filtered = []
    for pkm in all_pokemon:
        base_stats = pkm.get("stats", {})
        total_stats = sum(base_stats.values())

        # Exclure les stades finaux
        if not pkm.get("evolution", {}).get("evolves_to"):
            continue

        if stat_min <= total_stats <= stat_max:
            filtered.append({
                **pkm,
                "level": random.choice(level_range)
            })

    return random.choice(filtered) if filtered else random.choice(all_pokemon)
