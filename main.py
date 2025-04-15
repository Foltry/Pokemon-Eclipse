import pygame
import sys

from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from core.utils import quit_game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokémon Eclipse")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # MAJ logique
        # TODO: Ajouter mise à jour de la scène actuelle

        # Affichage
        screen.fill((0, 0, 0))  # écran noir temporaire
        pygame.display.flip()

        clock.tick(FPS)

    quit_game()

if __name__ == "__main__":
    from core.run_manager import RunManager

    run = RunManager()
    run.start_new_run()
    run.add_pokemon("001")
    run.add_item("Potion", 2)

    print("Run active ?", run.active)
    print("Équipe :", run.team)
    print("Objets :", run.items)

    # reset pour test
    run.reset()
    print("Run reset :", run.active, run.team, run.items)
