# ui/xp_bar.py

import pygame

class XPBar:
    """
    Barre d'expérience animée pour les Pokémon.

    Attributs :
        pos (tuple): Position (x, y) sur l'écran.
        max_xp (int): Expérience requise pour le niveau suivant.
        current_xp (int): Exp actuelle (valeur cible).
        displayed_xp (float): Exp affichée (animée progressivement).
    """

    def __init__(self, pos, max_xp):
        self.pos = pos
        self.size = (193, 5)
        self.max_xp = max_xp
        self.current_xp = 0
        self.displayed_xp = 0
        self.animation_duration = 0.7  # Durée totale (secondes)
        self.elapsed_time = 0

    def update(self, current_xp, dt=0):
        """
        Met à jour la progression affichée de la barre d'expérience.

        Args:
            current_xp (int): Valeur cible d'expérience.
            dt (float): Temps écoulé (en secondes).
        """
        self.current_xp = max(0, min(current_xp, self.max_xp))

        if self.displayed_xp != self.current_xp:
            direction = 1 if self.current_xp > self.displayed_xp else -1
            speed = abs(self.current_xp - self.displayed_xp) / self.animation_duration
            self.displayed_xp += direction * speed * dt

            if (direction == 1 and self.displayed_xp > self.current_xp) or \
               (direction == -1 and self.displayed_xp < self.current_xp):
                self.displayed_xp = self.current_xp

    def draw(self, surface):
        """
        Dessine la barre d'expérience sur l'écran.

        Args:
            surface (pygame.Surface): Surface sur laquelle dessiner.
        """
        x, y = self.pos
        width, height = self.size

        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))

        ratio = self.displayed_xp / self.max_xp if self.max_xp else 0
        fill_width = int(width * ratio)
        pygame.draw.rect(surface, (66, 135, 245), (x, y, fill_width, height))
