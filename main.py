import pygame
import sys
from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene  # Change ici si tu veux démarrer sur une autre scène
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokémon Eclipse")
    clock = pygame.time.Clock()

    # Lancement de la première scène (combat pour test)
    scene_manager = SceneManager()
    scene_manager.change_scene(BattleScene())

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        scene_manager.update(dt)
        scene_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
