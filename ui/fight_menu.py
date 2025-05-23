# ui/fight_menu.py

import os
import sys
import pygame

# Ajout du dossier parent au path (si exécuté directement)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.types_loader import get_type_index
from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from tools.assets import load_image

# === Initialisation test si exécuté directement ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test Menu FIGHT - Curseurs par type")

# === Couleurs et polices ===
TEXT_COLOR = (32, 32, 32)
PP_COLOR = (32, 32, 32)

font_path = os.path.join("assets", "fonts", "power clear.ttf")
pp_font_path = os.path.join("assets", "fonts", "power clear bold.ttf")
font = pygame.font.Font(font_path, 20)
pp_font = pygame.font.Font(pp_font_path, 18)


class FightMenu:
    """
    Menu de sélection d’attaque avec curseur par type et infos PP/type.
    """

    def __init__(self, surface, moves, font, pp_font):
        """
        Initialise le menu de combat.

        Args:
            surface (pygame.Surface): Surface sur laquelle dessiner.
            moves (list): Liste de 1 à 4 attaques (dicts avec name, type, pp...).
            font (pygame.font.Font): Police pour les noms.
            pp_font (pygame.font.Font): Police pour les PP.
        """
        self.surface = surface
        self.moves = moves
        self.font = font
        self.pp_font = pp_font
        self.selected_index = 0

        self.overlay = load_image("ui/battle/fightmenu/overlay_fight.png").convert_alpha()
        self.cursor = load_image("ui/battle/fightmenu/cursor_fight.png").convert_alpha()
        self.types_img = load_image("ui/battle/fightmenu/types.png").convert_alpha()

        self.button_positions = [(4, 294), (192, 294), (4, 336), (192, 336)]
        self.cursor_width = self.cursor.get_width() // 2
        self.cursor_height = self.cursor.get_height() // 19
        self.type_icon_width = 64
        self.type_icon_height = 28

    def move_cursor(self, direction):
        """Déplace le curseur selon la direction ('up', 'down', 'left', 'right')."""
        if direction == "left" and self.selected_index % 2 > 0:
            self.selected_index -= 1
        elif direction == "right" and self.selected_index % 2 < 1:
            self.selected_index += 1
        elif direction == "up" and self.selected_index > 1:
            self.selected_index -= 2
        elif direction == "down" and self.selected_index < 2:
            self.selected_index += 2

    def draw(self):
        """Dessine le menu complet avec les boutons, curseurs, types et PP."""
        if not self.surface:
            return

        self.surface.blit(self.overlay, (0, self.surface.get_height() - self.overlay.get_height()))

        # === Curseurs ===
        for i, (x, y) in enumerate(self.button_positions):
            if i >= len(self.moves):
                continue
            move_type = self.moves[i]["type"]
            type_index = get_type_index(move_type)
            if type_index >= 9:
                type_index += 1  # ➕ Pour corriger l’offset si "???" inséré dans l'image

            col = 1 if i == self.selected_index else 0
            src_rect = pygame.Rect(col * self.cursor_width, type_index * self.cursor_height, self.cursor_width, self.cursor_height)
            self.surface.blit(self.cursor, (x, y), src_rect)

        # === Texte des attaques ===
        for i, move in enumerate(self.moves):
            base_x, base_y = self.button_positions[i]
            name_surf = self.font.render(move["name"], True, TEXT_COLOR)
            text_x = base_x + (self.cursor_width - name_surf.get_width()) // 2
            self.surface.blit(name_surf, (text_x, base_y + 10))

        # === Affichage des infos du move sélectionné ===
        if self.moves:
            idx = min(self.selected_index, len(self.moves) - 1)
            move = self.moves[idx]
            type_idx = get_type_index(move["type"])
            if type_idx >= 9:
                type_idx += 1

            type_icon_x = 416
            type_icon_y = self.surface.get_height() - 75
            type_src = pygame.Rect(0, type_idx * self.type_icon_height, self.type_icon_width, self.type_icon_height)
            self.surface.blit(self.types_img, (type_icon_x, type_icon_y), type_src)

            pp_text = f"PP: {move['pp']}/{move['max_pp']}"
            pp_surf = self.pp_font.render(pp_text, True, PP_COLOR)
            pp_x = type_icon_x + (self.type_icon_width - pp_surf.get_width()) // 2
            pp_y = type_icon_y + self.type_icon_height + 10
            self.surface.blit(pp_surf, (pp_x, pp_y))


# === Test rapide ===
if __name__ == "__main__":
    test_moves = [
        {"name": "Flammèche", "type": "Feu", "pp": 15, "max_pp": 15},
        {"name": "Charge", "type": "Normal", "pp": 3, "max_pp": 20},
        {"name": "Griffe", "type": "Normal", "pp": 10, "max_pp": 20},
        {"name": "Exploforce", "type": "Combat", "pp": 0, "max_pp": 5},
    ]
    fight_menu = FightMenu(screen, test_moves, font, pp_font)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    fight_menu.move_cursor("left")
                elif event.key == pygame.K_RIGHT:
                    fight_menu.move_cursor("right")
                elif event.key == pygame.K_UP:
                    fight_menu.move_cursor("up")
                elif event.key == pygame.K_DOWN:
                    fight_menu.move_cursor("down")

        fight_menu.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
