import pygame
import sys
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene

def main():
    pygame.init()
    pygame.display.set_caption("Pokémon Eclipse")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    scene_manager = SceneManager()
    scene_manager.change_scene(BattleScene())  # Scène de test par défaut

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time en secondes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
