import pygame
import sys

from core.scene_manager import SceneManager
from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from scene.menu_scene import MenuScene  # ← On revient au menu principal

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokémon Eclipse")

    clock = pygame.time.Clock()
    scene_manager = SceneManager()
    scene_manager.change_scene(MenuScene())  # ← Lance le menu principal

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
