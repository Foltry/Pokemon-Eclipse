# ui/animated_text.py

import pygame

class AnimatedText:
    """
    Classe permettant d’afficher un texte progressivement (lettre par lettre).

    Args:
        text (str): Texte complet à afficher.
        font (pygame.font.Font): Police utilisée pour le rendu.
        pos (tuple): Position (x, y) d’affichage.
        speed (int): Nombre de caractères affichés par seconde.
    """

    def __init__(self, text, font, pos, speed=50):
        self.full_text = text
        self.font = font
        self.pos = pos
        self.speed = speed
        self.start_time = pygame.time.get_ticks()
        self.done = False

    def draw(self, surface):
        """
        Affiche le texte animé sur une surface donnée.

        Args:
            surface (pygame.Surface): Surface sur laquelle dessiner.
        """
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        nb_chars = min(int(elapsed * self.speed), len(self.full_text))
        visible_text = self.full_text[:nb_chars]

        if nb_chars == len(self.full_text):
            self.done = True

        text_surface = self.font.render(visible_text, True, (0, 0, 0))
        surface.blit(text_surface, self.pos)
