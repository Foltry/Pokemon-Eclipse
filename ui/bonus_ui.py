# ui/bonus_ui.py

import pygame
import os
import unicodedata
from data.items_loader import get_item_by_name

FONTS = os.path.join("assets", "fonts")
SPRITE_PATH = os.path.join("assets", "sprites", "items")
UI_PATH = os.path.join("assets", "ui", "battle")

def normalize_item_filename(name):
    name = name.lower().replace(" ", "-")
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    return name + ".png"

class BonusUI:
    def __init__(self, pos=(300, 270), spacing=22):
        font_path = os.path.join(FONTS, "power clear.ttf")
        self.font_title = pygame.font.Font(font_path, 24)
        self.font_items = pygame.font.Font(font_path, 22)
        self.pos = pos
        self.spacing = spacing
        self.items = []
        self.selected = 0

        self.bonus_bg_path = os.path.join(UI_PATH, "dialogue_box_bonus.png")
        self.bonus_bg = None

    def set_items(self, items):
        self.items = items
        self.selected = 0

    def draw(self, screen):
        x, y = self.pos

        if self.bonus_bg is None:
            self.bonus_bg = pygame.image.load(self.bonus_bg_path).convert_alpha()

        screen.blit(self.bonus_bg, (x - 30, y - 6))

        for i, item_name in enumerate(self.items):
            line_y = y + 5 + i * self.spacing

            # Charger sprite uniquement si item connu
            item_data = get_item_by_name(item_name)
            if item_data and "sprite" in item_data:
                sprite_path = os.path.join(SPRITE_PATH, item_data["sprite"])
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    screen.blit(sprite, (x - 20, line_y))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), (x - 20, line_y, 32, 32))
            else:
                pygame.draw.rect(screen, (100, 100, 100), (x - 20, line_y, 32, 32))

            color = (255, 0, 0) if i == self.selected else (0, 0, 0)
            name_surface = self.font_items.render(item_name, True, color)
            screen.blit(name_surface, (x + 10, line_y + 4))

    def move_selection(self, direction):
        if not self.items:
            return
        self.selected = (self.selected + direction) % len(self.items)

    def get_selected_item(self):
        return self.items[self.selected] if self.items else None
