# ui/bonus_ui.py

import os
import pygame
import unicodedata
from data.items_loader import get_item_by_name

# === Chemins ===
FONTS = os.path.join("assets", "fonts")
SPRITE_PATH = os.path.join("assets", "sprites", "items")
UI_PATH = os.path.join("assets", "ui", "battle")

def normalize_item_filename(name):
    """
    Normalise un nom d'objet pour correspondre à un nom de fichier image.
    """
    name = name.lower().replace(" ", "-")
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    return name + ".png"

class BonusUI:
    """
    Interface de sélection de bonus après un combat.
    Affiche une liste d’objets, leur icône, et permet la sélection via clavier.
    """

    def __init__(self, pos=(300, 270), spacing=22):
        """
        Initialise l’interface bonus.

        Args:
            pos (tuple): Position de départ (x, y) sur l’écran.
            spacing (int): Espacement vertical entre chaque ligne.
        """
        font_path = os.path.join(FONTS, "power clear.ttf")
        self.font_title = pygame.font.Font(font_path, 24)
        self.font_items = pygame.font.Font(font_path, 22)

        self.pos = pos
        self.spacing = spacing
        self.items = []
        self.selected = 0

        self.bonus_bg_path = os.path.join(UI_PATH, "dialogue_box_bonus.png")
        self.bonus_bg = None  # Chargé à la première frame

    def set_items(self, items):
        """
        Définit les objets à afficher dans le menu.

        Args:
            items (list[str]): Noms des objets.
        """
        self.items = items
        self.selected = 0

    def draw(self, screen):
        """
        Affiche l’interface bonus sur l’écran.

        Args:
            screen (pygame.Surface): Surface cible.
        """
        x, y = self.pos

        if self.bonus_bg is None:
            self.bonus_bg = pygame.image.load(self.bonus_bg_path).convert_alpha()

        screen.blit(self.bonus_bg, (x - 30, y - 6))

        for i, item_name in enumerate(self.items):
            line_y = y + 5 + i * self.spacing

            # Tentative de chargement du sprite de l'objet
            item_data = get_item_by_name(item_name)
            if item_data and "sprite" in item_data:
                sprite_path = os.path.join(SPRITE_PATH, item_data["sprite"])
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    screen.blit(sprite, (x - 20, line_y))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), (x - 20, line_y, 32, 32))  # fallback
            else:
                pygame.draw.rect(screen, (100, 100, 100), (x - 20, line_y, 32, 32))  # fallback générique

            # Affichage du nom
            color = (255, 0, 0) if i == self.selected else (0, 0, 0)
            name_surface = self.font_items.render(item_name, True, color)
            screen.blit(name_surface, (x + 10, line_y + 4))

    def move_selection(self, direction):
        """
        Change la sélection actuelle.

        Args:
            direction (int): +1 pour descendre, -1 pour monter.
        """
        if not self.items:
            return
        self.selected = (self.selected + direction) % len(self.items)

    def get_selected_item(self):
        """
        Retourne le nom de l’objet actuellement sélectionné.

        Returns:
            str | None
        """
        return self.items[self.selected] if self.items else None
