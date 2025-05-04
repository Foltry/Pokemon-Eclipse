# scene/gameover_scene.py

import pygame
from core.scene_manager import Scene
from scene.menu_scene import MenuScene

FONT_PATH = "assets/fonts/power clear.ttf"
TITLE_COLOR = (255, 0, 0)

class GameOverScene(Scene):
    """
    Scène affichée après une défaite totale du joueur.
    Affiche un écran 'Game Over' pendant quelques secondes
    puis retourne automatiquement au menu principal.
    """

    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(FONT_PATH, 48)
        self.timer = 0
        self.duration = 3000  # Durée en millisecondes (3 secondes)

    def on_enter(self):
        """Réinitialise le minuteur à l'entrée dans la scène."""
        self.timer = 0

    def update(self, dt):
        """
        Met à jour le minuteur et change de scène après expiration.
        """
        self.timer += dt
        if self.timer >= self.duration:
            self.manager.change_scene(MenuScene())

    def draw(self, screen):
        """
        Affiche le message 'Game Over' au centre de l'écran.
        """
        screen.fill((0, 0, 0))  # Fond noir
        title_surface = self.font_title.render("Game Over", True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(256, 180))
        screen.blit(title_surface, title_rect)
