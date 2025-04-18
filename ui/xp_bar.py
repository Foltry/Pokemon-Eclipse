import pygame

class XPBar:
    def __init__(self, pos, max_xp):
        self.pos = pos
        self.size = (193, 5)
        self.max_xp = max_xp
        self.current_xp = max_xp

    def update(self, current_xp):
        self.current_xp = max(0, min(current_xp, self.max_xp))

    def draw(self, surface):
        x, y = self.pos
        width, height = self.size

        # Fond gris foncé
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))

        # Barre bleue selon XP
        ratio = self.current_xp / self.max_xp if self.max_xp else 0
        pygame.draw.rect(surface, (66, 135, 245), (x, y, int(width * ratio), height))
