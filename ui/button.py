import pygame

class UIButton:
    """
    Bouton interactif simple avec effet de survol et déclenchement de callback.
    """

    def __init__(self, rect, text, font, callback, base_color=(255, 255, 255), hover_color=(200, 200, 200)):
        """
        Initialise le bouton.

        Args:
            rect (tuple): (x, y, width, height) définissant la position et la taille.
            text (str): Texte affiché sur le bouton.
            font (pygame.font.Font): Police utilisée.
            callback (callable): Fonction appelée lors du clic.
            base_color (tuple): Couleur normale.
            hover_color (tuple): Couleur au survol.
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.base_color = base_color
        self.hover_color = hover_color
        self.hovered = False

    def update(self, mouse_pos, mouse_click):
        """
        Met à jour l'état de survol et déclenche l’action si cliqué.

        Args:
            mouse_pos (tuple): Position actuelle de la souris.
            mouse_click (bool): True si le bouton de souris est cliqué.
        """
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click:
            self.callback()

    def draw(self, surface):
        """
        Affiche le bouton sur la surface donnée.

        Args:
            surface (pygame.Surface): Surface cible.
        """
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
