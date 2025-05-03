import pygame
import sys

from core.scene_manager import SceneManager
from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.run_manager import run_manager
from scene.gameover_scene import GameOverScene
from data.items_loader import get_all_items

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokémon Eclipse")

    clock = pygame.time.Clock()
    scene_manager = SceneManager()

    items = get_all_items()
    for item in items:
        run_manager.add_item(item)


    scene_manager.change_scene(GameOverScene())

    running = True
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
