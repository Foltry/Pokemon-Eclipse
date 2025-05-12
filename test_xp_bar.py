import pygame
import logging

from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene
from core.run_manager import run_manager
from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves
from data.items_loader import get_all_items
from core.config import *

# Setup logging dans un fichier
logging.basicConfig(
    filename="xp_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialisation Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# === Construction du Pokémon test (Rattata Nv.5 avec 200 XP) ===
rattata = get_pokemon_by_id(19)
rattata_data = {
    "id": rattata["id"],
    "name": rattata["name"],
    "level": 5,
    "xp": 200,  # Juste avant le niveau 6 (216)
    "types": rattata["types"],
    "stats": rattata["stats"].copy(),
    "base_stats": rattata["stats"].copy(),
    "sprites": rattata["sprites"],
    "gender": "♀",
    "moves": get_learnable_moves(19, 5),
    "hp": rattata["stats"]["hp"]
}
run_manager.start_new_run()
run_manager.add_pokemon_to_team(rattata_data)

for item in get_all_items():
    run_manager.add_item(item)

# === Fonction de logging XP (hookée dans update_ally_xp manuellement si besoin) ===
def log_xp_state(pokemon):
    level = pokemon.get("level", 1)
    xp = pokemon.get("xp", 0)
    next_xp = (level + 1) ** 3
    prev_xp = level ** 3
    progress = xp - prev_xp
    needed = next_xp - prev_xp

    logging.debug(
        f"[XP CHECK] {pokemon['name']} | XP={xp} | Level={level} | "
        f"Progress={progress}/{needed} | XP_prev={prev_xp} XP_next={next_xp}"
    )

log_xp_state(rattata_data)

# === Lancement de la scène de combat ===
manager = SceneManager()
manager.change_scene(BattleScene())

# === Boucle de jeu ===
running = True
while running:
    dt = clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.handle_event(event)

    manager.update(dt)
    manager.draw(screen)

    pygame.display.flip()

    # Log en continu (facultatif)
    log_xp_state(run_manager.get_team()[0])

pygame.quit()
