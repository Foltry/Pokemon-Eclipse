# ui/attack_effects.py

import pygame

class AttackEffect:
    """
    Effet visuel temporaire pour simuler un impact d’attaque.

    Args:
        pos (tuple): Position (x, y) du centre de l’effet.
        duration (int): Durée totale de l’effet en millisecondes.
    """

    def __init__(self, pos, duration=300):
        self.pos = pos
        self.duration = duration
        self.elapsed = 0
        self.active = True
        self.radius = 0

    def update(self, dt):
        """
        Met à jour l’état de l’effet (durée écoulée, rayon).

        Args:
            dt (int): Temps écoulé depuis la dernière frame (en ms).
        """
        if not self.active:
            return

        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1)
        self.radius = int(30 * progress)

        if self.elapsed >= self.duration:
            self.active = False

    def draw(self, surface):
        """
        Dessine l’effet circulaire sur la surface donnée.

        Args:
            surface (pygame.Surface): Surface cible.
        """
        if not self.active:
            return

        pygame.draw.circle(surface, (255, 255, 0), self.pos, self.radius, 2)
