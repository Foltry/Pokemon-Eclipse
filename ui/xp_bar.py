import pygame

class XPBar:
    """
    Barre d'expérience animée pour les Pokémon.
    """
    def __init__(self, pos, max_xp):
        self.pos = pos
        self.max_xp = max_xp
        self.current_xp = 0
        self.displayed_xp = 0

        self.start_xp = 0
        self.target_xp = 0
        self.animation_elapsed = 0
        self.animation_duration = 0.7
        self.animating = False

        self.bar_width = 192
        self.bar_height = 5
        self.bar_color = (102, 204, 255)

    def update(self, xp_value, dt):
        if not hasattr(self, "target_xp"):
            self.start_xp = self.displayed_xp = self.target_xp = self.current_xp = 0
            self.animating = False
            self.animation_elapsed = 0

        self.current_xp = xp_value

        if xp_value != self.target_xp:
            self.start_xp = self.displayed_xp
            self.target_xp = xp_value
            self.animation_elapsed = 0
            self.animating = True

        if self.animating:
            self.animation_elapsed += dt
            t = min(self.animation_elapsed / self.animation_duration, 1.0)
            self.displayed_xp = self.start_xp + (self.target_xp - self.start_xp) * t
            if t >= 1.0:
                self.displayed_xp = self.target_xp
                self.animating = False

    def draw(self, surface):
        x, y = self.pos
        pygame.draw.rect(surface, (30, 30, 30), (x, y, self.bar_width, self.bar_height))
        ratio = self.displayed_xp / self.max_xp if self.max_xp else 0
        fill_width = int(self.bar_width * ratio)
        pygame.draw.rect(surface, self.bar_color, (x, y, fill_width, self.bar_height))

    def reset_displayed_xp(self, force_value=0):
        self.start_xp = force_value
        self.displayed_xp = force_value
        self.target_xp = force_value
        self.animating = False
        self.animation_elapsed = 0
