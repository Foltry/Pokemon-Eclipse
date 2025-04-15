import pygame
import sys

from core.scene_manager import SceneManager
from scene.starter_scene import StarterScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 360))
    pygame.display.set_caption("Pokémon Eclipse")

    clock = pygame.time.Clock()
    scene_manager = SceneManager()
    scene_manager.change_scene(StarterScene())  # Lancement initial

    while True:
        dt = clock.tick(60) / 1000  # Temps écoulé (sec)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
