import pygame

class HealthBar:
    def __init__(self, pos, size, max_hp):
        self.pos = pos
        self.size = size
        self.max_hp = max_hp
        self.current_hp = max_hp

    def update(self, current_hp):
        self.current_hp = max(0, min(current_hp, self.max_hp))

    def draw(self, surface):
        x, y = self.pos
        w, h = self.size
        ratio = self.current_hp / self.max_hp
        bar_color = (0, 255, 0) if ratio > 0.5 else (255, 255, 0) if ratio > 0.2 else (255, 0, 0)

        # Background
        pygame.draw.rect(surface, (50, 50, 50), (x, y, w, h))
        # Filled bar
        pygame.draw.rect(surface, bar_color, (x, y, w * ratio, h))
        # Border
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
