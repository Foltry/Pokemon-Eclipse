import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.run_manager import run_manager
from core.config import *
from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene
from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves
from data.items_loader import get_all_items

def setup_test_team():
    bulbizarre = get_pokemon_by_id(1)
    bulbizarre_data = {
        "id": bulbizarre["id"],
        "name": bulbizarre["name"],
        "level": 15,
        "xp": 4061,
        "types": bulbizarre["types"],
        "stats": bulbizarre["stats"].copy(),
        "base_stats": bulbizarre["stats"].copy(),
        "sprites": bulbizarre["sprites"],
        "gender": "♂",
        "moves": get_learnable_moves(1, 15),
        "hp": bulbizarre["stats"]["hp"]
    }

    run_manager.team = [bulbizarre_data]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Évolution Bulbizarre")

    setup_test_team()
    scene_manager = SceneManager()
    scene_manager.change_scene(BattleScene())

    clock = pygame.time.Clock()
    running = True
    items = get_all_items()
    for item in items:
        run_manager.add_item(item)
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
