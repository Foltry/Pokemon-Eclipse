import pygame

class UIButton:
    def __init__(self, rect, text, font, callback, base_color=(255,255,255), hover_color=(200,200,200)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.base_color = base_color
        self.hover_color = hover_color
        self.hovered = False

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click:
            self.callback()

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
