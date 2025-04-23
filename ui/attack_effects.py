# ui/attack_effects.py

import pygame

class AttackEffect:
    def __init__(self, pos, duration=300):
        self.pos = pos
        self.duration = duration
        self.elapsed = 0
        self.active = True
        self.radius = 0

    def update(self, dt):
        if not self.active:
            return
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1)
        self.radius = int(30 * progress)
        if self.elapsed >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        pygame.draw.circle(surface, (255, 255, 0), self.pos, self.radius, 2)
