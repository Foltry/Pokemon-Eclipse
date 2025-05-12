import pygame
import logging

from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene
from core.run_manager import run_manager
from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves
from data.items_loader import get_all_items
from core.config import *

# Setup logging XP
logging.basicConfig(
    filename="xp_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# === Pokémon test : Bulbizarre niveau 15 avec 4000 XP (Niveau 15 = 3375, 16 = 4096) ===
bulbizarre = get_pokemon_by_id(1)
bulbizarre_data = {
    "id": bulbizarre["id"],
    "name": bulbizarre["name"],
    "level": 15,
    "xp": 4086,  # Juste avant niveau 16
    "types": bulbizarre["types"],
    "stats": bulbizarre["stats"].copy(),
    "base_stats": bulbizarre["stats"].copy(),
    "sprites": bulbizarre["sprites"],
    "gender": "♂",
    "moves": get_learnable_moves(1, 15),
    "hp": bulbizarre["stats"]["hp"]
}

# Init run
run_manager.start_new_run()
run_manager.add_pokemon_to_team(bulbizarre_data)

# Ajoute tous les objets au sac
for item in get_all_items():
    run_manager.add_item(item)

# Combat
manager = SceneManager()
manager.change_scene(BattleScene())

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
pygame.quit()
