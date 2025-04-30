import pygame

class HealthBar:
    def __init__(self, pos, size, max_hp, colors=None):
        self.x, self.y = pos
        self.width, self.height = size
        self.max_hp = max_hp
        self.current_hp = max_hp

        # Couleurs customisables
        self.colors = colors or {
            "high": (0, 192, 0),
            "medium": (232, 192, 0),
            "low": (240, 64, 48)
        }

    def update(self, current_hp):
        self.current_hp = max(0, min(current_hp, self.max_hp))

    def draw(self, surface):
        if self.max_hp == 0:
            return

        ratio = self.current_hp / self.max_hp
        if ratio > 0.5:
            color = self.colors["high"]
        elif ratio > 0.2:
            color = self.colors["medium"]
        else:
            color = self.colors["low"]

        fill_width = int(self.width * ratio)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
        pygame.draw.rect(surface, color, fill_rect)
