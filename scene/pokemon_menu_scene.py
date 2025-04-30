import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import config
from ui.pokemon_menu import PokemonMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Scène - Menu Pokémon")
    clock = pygame.time.Clock()

    menu = PokemonMenu()

    running = True
    while running:
        dt = clock.tick(60)
        menu.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                menu.handle_input(event)

        menu.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
