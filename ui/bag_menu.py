# ui/bag_menu.py

import pygame
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.items_loader import get_item_sprite, get_item_effect, get_item_category
from battle.use_item import use_item_on_pokemon
from core.run_manager import run_manager


class BagMenu:
    """
    Menu du sac affichant l'inventaire, permettant d'utiliser des objets.
    """

    def __init__(self, inventory):
        self.empty_mode = not inventory
        self.inventory = [{"name": "FERMER LE SAC", "quantity": 0}] if self.empty_mode else inventory

        self.selected_index = 0
        self.scroll_offset = 0
        self.message_queue = []

        # === Assets ===
        self.background = self.load_image("assets/ui/Bag/bg_items.png", (0, 0, 0))
        self.cursor_img = self.load_image("assets/ui/Bag/cursor.png", (255, 0, 0))
        self.bag_item_img = self.load_image("assets/ui/Bag/bag_items.png", (100, 100, 255))

        self.font_items = pygame.font.Font("assets/fonts/power clear.ttf", 22)
        self.font_description = pygame.font.Font("assets/fonts/power clear bold.ttf", 20)

        # === Constantes d'affichage ===
        self.LIST_START_X = 200
        self.LIST_START_Y = 35
        self.ITEM_SPACING_Y = 35
        self.VISIBLE_ITEM_COUNT = 7
        self.CURSOR_OFFSET_X = -16
        self.DESCRIPTION_X = 90
        self.DESCRIPTION_Y = 290
        self.QUANTITY_X = 400
        self.ICON_BOX_POS = (21, 308)
        self.ICON_BOX_SIZE = (56, 56)

    def load_image(self, path, fallback_color=(255, 0, 0)):
        """Charge une image ou retourne un carré de secours coloré."""
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            surface = pygame.Surface((32, 32))
            surface.fill(fallback_color)
            return surface

    def queue_message(self, text):
        """Ajoute un message à la file (ex: objet inutile)."""
        self.message_queue.append(text)

    def handle_event(self, event, scene_manager):
        """Gère les interactions clavier avec le menu du sac."""
        if event.type != pygame.KEYDOWN:
            return

        # --- Si un message est affiché ---
        if self.message_queue:
            if event.key == pygame.K_RETURN:
                self.message_queue.pop(0)
            return

        # --- Retour arrière ---
        if event.key == pygame.K_ESCAPE:
            scene_manager.go_back()
            return

        # --- Navigation ---
        if event.key in (pygame.K_DOWN, pygame.K_s):
            if self.selected_index < len(self.inventory) - 1:
                self.selected_index += 1
                if self.selected_index - self.scroll_offset >= self.VISIBLE_ITEM_COUNT:
                    self.scroll_offset += 1

        elif event.key in (pygame.K_UP, pygame.K_z):
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset -= 1

        # --- Utilisation d’un objet ---
        elif event.key == pygame.K_RETURN:
            if self.empty_mode or self.inventory[self.selected_index]["name"] == "FERMER LE SAC":
                scene_manager.go_back()
                return

            selected_item = self.inventory[self.selected_index]
            item_name = selected_item["name"]
            category = get_item_category(item_name)

            current_scene = scene_manager.scene_stack[-2] if len(scene_manager.scene_stack) > 1 else None
            if not current_scene:
                scene_manager.go_back()
                return

            # --- Poké Ball ---
            if category == "standard-balls":
                current_scene.throw_ball(item_name)
                self.decrement_item(selected_item)
                scene_manager.go_back()
                return

            # --- Soin ou statut ---
            pokemon = run_manager.get_team()[0]
            result = use_item_on_pokemon(item_name, pokemon)

            if result["success"]:
                self.decrement_item(selected_item)
                if hasattr(current_scene, "ally_hp"):
                    current_scene.ally_hp = pokemon["hp"]

                current_scene.queue_message(result["message"])
                current_scene.message_queue.append(current_scene.enemy_turn)
                scene_manager.go_back()
            else:
                self.queue_message(result["message"])

    def decrement_item(self, item):
        """Diminue la quantité d’un objet, et le retire si elle atteint zéro."""
        item["quantity"] -= 1
        if item["quantity"] <= 0:
            self.inventory.pop(self.selected_index)

    def update(self, dt):
        pass  # Placeholder pour animation future

    def draw(self, screen):
        """Affiche le menu complet du sac sur l’écran."""
        screen.blit(self.background, (0, 0))
        screen.blit(self.bag_item_img, (30, 17))

        if self.message_queue:
            self.draw_message(screen)
            return

        # === Affichage des objets ===
        for i in range(self.VISIBLE_ITEM_COUNT):
            item_index = self.scroll_offset + i
            if item_index >= len(self.inventory):
                break

            item = self.inventory[item_index]
            y = self.LIST_START_Y + i * self.ITEM_SPACING_Y

            name_surf = self.font_items.render(item["name"], True, (0, 0, 0))
            screen.blit(name_surf, (self.LIST_START_X, y))

            if not (self.empty_mode or item["name"] == "FERMER LE SAC"):
                qty_surf = self.font_items.render(f"x{item['quantity']}", True, (0, 0, 0))
                screen.blit(qty_surf, (self.QUANTITY_X, y))

            if item_index == self.selected_index:
                cursor_rect = self.cursor_img.get_rect()
                cursor_pos = (self.LIST_START_X + self.CURSOR_OFFSET_X, y + (name_surf.get_height() - cursor_rect.height) // 2)
                screen.blit(self.cursor_img, cursor_pos)

        # === Affichage de l’icône et de la description ===
        if not self.empty_mode and self.inventory[self.selected_index]["name"] != "FERMER LE SAC":
            selected_item = self.inventory[self.selected_index]
            sprite_path = get_item_sprite(selected_item["name"])

            # Icône
            if os.path.exists(sprite_path):
                icon = pygame.image.load(sprite_path).convert_alpha()
                icon = pygame.transform.scale(icon, (icon.get_width() * 2, icon.get_height() * 2))
                icon_x = self.ICON_BOX_POS[0] + (self.ICON_BOX_SIZE[0] - icon.get_width()) // 2
                icon_y = self.ICON_BOX_POS[1] + (self.ICON_BOX_SIZE[1] - icon.get_height()) // 2
                screen.blit(icon, (icon_x, icon_y))
            else:
                fallback = pygame.Surface((32, 32))
                fallback.fill((150, 150, 150))
                screen.blit(fallback, self.ICON_BOX_POS)

            # Description
            effect = get_item_effect(selected_item["name"]) or "Pas de description disponible."
            self.draw_multiline_text(screen, effect, self.DESCRIPTION_X, self.DESCRIPTION_Y, 478 - self.DESCRIPTION_X)

    def draw_message(self, screen):
        """Affiche un message avec retour à la ligne automatique."""
        if not self.message_queue:
            return

        self.draw_multiline_text(
            screen,
            self.message_queue[0],
            start_x=91,
            start_y=324,
            max_width=387
        )

    def draw_multiline_text(self, screen, text, start_x, start_y, max_width):
        """Affiche du texte multiligne avec gestion de largeur."""
        words = text.split()
        line = ""
        y_offset = 0

        for word in words:
            test_line = f"{line}{word} "
            if self.font_description.size(test_line)[0] > max_width:
                rendered = self.font_description.render(line.strip(), True, (255, 255, 255))
                screen.blit(rendered, (start_x, start_y + y_offset))
                y_offset += rendered.get_height() + 5
                line = f"{word} "
            else:
                line = test_line

        if line:
            rendered = self.font_description.render(line.strip(), True, (255, 255, 255))
            screen.blit(rendered, (start_x, start_y + y_offset))
