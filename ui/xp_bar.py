import pygame

class XPBar:
    def __init__(self, pos, max_xp):
        self.pos = pos
        self.size = (193, 5)
        self.max_xp = max_xp
        self.current_xp = 0           # Valeur réelle
        self.displayed_xp = 0         # Valeur affichée (animée)
        self.animation_duration = 0.7 # Durée totale de l'animation (1s)
        self.elapsed_time = 0

    def update(self, current_xp, dt=0):
        self.current_xp = max(0, min(current_xp, self.max_xp))

        if self.displayed_xp != self.current_xp:
            direction = 1 if self.current_xp > self.displayed_xp else -1
            speed = abs(self.current_xp - self.displayed_xp) / self.animation_duration
            self.displayed_xp += direction * speed * dt

            if (direction == 1 and self.displayed_xp > self.current_xp) or \
               (direction == -1 and self.displayed_xp < self.current_xp):
                self.displayed_xp = self.current_xp

    def draw(self, surface):
        x, y = self.pos
        width, height = self.size

        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))

        ratio = self.displayed_xp / self.max_xp if self.max_xp else 0
        fill_width = int(width * ratio)
        pygame.draw.rect(surface, (66, 135, 245), (x, y, fill_width, height))
