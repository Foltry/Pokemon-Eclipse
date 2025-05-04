import pygame

class HealthBar:
    def __init__(self, pos, size, max_hp, colors=None):
        self.x, self.y = pos
        self.width, self.height = size
        self.max_hp = max_hp

        self.current_hp = max_hp
        self.displayed_hp = max_hp

        self.start_hp = max_hp
        self.target_hp = max_hp
        self.animating = False
        self.animation_elapsed = 0
        self.animation_duration = 0.7

        self.colors = colors or {
            "high": (0, 192, 0),
            "medium": (232, 192, 0),
            "low": (240, 64, 48)
        }

    def update(self, current_hp, dt):
        current_hp = max(0, min(current_hp, self.max_hp))
        self.current_hp = current_hp

        if current_hp != self.target_hp:
            self.start_hp = self.displayed_hp
            self.target_hp = current_hp
            self.animation_elapsed = 0
            self.animating = True

        if self.animating:
            self.animation_elapsed += dt
            t = min(self.animation_elapsed / self.animation_duration, 1.0)
            self.displayed_hp = self.start_hp + (self.target_hp - self.start_hp) * t
            if t >= 1.0:
                self.displayed_hp = self.target_hp
                self.animating = False

    def draw(self, surface):
        if self.max_hp <= 0:
            return

        ratio = self.displayed_hp / self.max_hp
        if ratio > 0.5:
            color = self.colors["high"]
        elif ratio > 0.2:
            color = self.colors["medium"]
        else:
            color = self.colors["low"]

        fill_width = int(self.width * ratio)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
        pygame.draw.rect(surface, color, fill_rect)
