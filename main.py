import pygame
import sys

from core.scene_manager import SceneManager
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from core.run_manager import run_manager
from scene.gameover_scene import GameOverScene
from data.items_loader import get_all_items

def main():
    """
    Point d'entrée principal du jeu.
    Initialise Pygame, charge les objets, configure la scène initiale et lance la boucle principale.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokémon Eclipse")

    clock = pygame.time.Clock()
    scene_manager = SceneManager()

    # Charger tous les objets dans l'inventaire
    for item in get_all_items():
        run_manager.add_item(item)

    # Lancer la première scène (Game Over ici pour test/démo)
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
