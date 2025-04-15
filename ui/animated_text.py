import pygame

class AnimatedText:
    def __init__(self, text, font, pos, speed=50):
        self.full_text = text
        self.font = font
        self.pos = pos
        self.speed = speed  # lettres/sec
        self.start_time = pygame.time.get_ticks()
        self.done = False

    def draw(self, surface):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        nb_chars = min(int(elapsed * self.speed), len(self.full_text))
        visible_text = self.full_text[:nb_chars]
        if nb_chars == len(self.full_text):
            self.done = True
        text_surface = self.font.render(visible_text, True, (255, 255, 255))
        surface.blit(text_surface, self.pos)
