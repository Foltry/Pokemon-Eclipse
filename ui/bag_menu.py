# ui/bag_menu.py

import pygame
import os

from data.items_loader import get_item_sprite, get_item_effect
from battle.use_item import use_item_on_pokemon
from core.run_manager import run_manager


class BagMenu:
    def __init__(self, inventory):
        # --- Inventaire ---
        self.empty_mode = not inventory
        if self.empty_mode:
            self.inventory = [{"name": "FERMER LE SAC", "quantity": 0}]
        else:
            self.inventory = inventory

        # --- Sélection & Scroll ---
        self.selected_index = 0
        self.scroll_offset = 0

        # --- Chargement assets et polices (fixes) ---
        from core import config
        self.background = pygame.image.load("assets/ui/Bag/bg_items.png").convert_alpha()
        self.cursor_img = pygame.image.load("assets/ui/Bag/cursor.png").convert_alpha()
        self.bag_item_img = pygame.image.load("assets/ui/Bag/bag_items.png").convert_alpha()

        self.font_items = pygame.font.Font("assets/fonts/power clear.ttf", 22)
        self.font_description = pygame.font.Font("assets/fonts/power clear bold.ttf", 20)

        # --- Constantes d'affichage ---
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
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            surface = pygame.Surface((32, 32))
            surface.fill(fallback_color)
            return surface

    def handle_event(self, event, scene_manager):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scene.battle_scene import BattleScene
                scene_manager.change_scene(BattleScene())

            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(self.inventory) - 1:
                    self.selected_index += 1
                    if self.selected_index - self.scroll_offset >= self.VISIBLE_ITEM_COUNT:
                        self.scroll_offset += 1

            elif event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset -= 1

            elif event.key == pygame.K_RETURN:
                if self.empty_mode:
                    from scene.battle_scene import BattleScene
                    scene_manager.change_scene(BattleScene())
                else:
                    selected_item = self.inventory[self.selected_index]
                    item_name = selected_item["name"]

                    # Prendre le premier Pokémon de l'équipe
                    if not run_manager.get_team():
                        print("Vous n'avez pas de Pokémon dans votre équipe.")
                        return

                    pokemon = run_manager.get_team()[0]

                    result = use_item_on_pokemon(item_name, pokemon)

                    if result["success"]:
                        print(result["message"])
                        # Diminuer la quantité
                        selected_item["quantity"] -= 1
                        if selected_item["quantity"] <= 0:
                            self.inventory.pop(self.selected_index)
                            # Ajustement curseur si besoin
                            if self.selected_index >= len(self.inventory):
                                self.selected_index = max(0, len(self.inventory) - 1)
                            if not self.inventory:
                                self.empty_mode = True
                                self.inventory = [{"name": "FERMER LE SAC", "quantity": 0}]
                    else:
                        print(result["message"])



    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.bag_item_img, (30, 17))

        if not self.inventory:
            # Cas sans objets
            empty_text = self.font_items.render("Votre sac est vide.", True, (255, 255, 255))
            screen.blit(empty_text, (self.LIST_START_X, self.LIST_START_Y))
            return

        # Affichage de la liste
        for i in range(self.VISIBLE_ITEM_COUNT):
            item_index = self.scroll_offset + i
            if item_index >= len(self.inventory):
                break

            item = self.inventory[item_index]
            x = self.LIST_START_X
            y = self.LIST_START_Y + i * self.ITEM_SPACING_Y

            name_surface = self.font_items.render(item["name"], True, (0, 0, 0))
            quantity_surface = self.font_items.render(f"x{item['quantity']}", True, (0, 0, 0))

            screen.blit(name_surface, (x, y))
            screen.blit(quantity_surface, (self.QUANTITY_X, y))

            if item_index == self.selected_index:
                cursor_rect = self.cursor_img.get_rect()
                cursor_pos = (x + self.CURSOR_OFFSET_X, y + (name_surface.get_height() - cursor_rect.height) // 2)
                screen.blit(self.cursor_img, cursor_pos)

        # Icône de l'objet sélectionné
        selected_item = self.inventory[self.selected_index]
        sprite_path = get_item_sprite(selected_item["name"])

        if os.path.exists(sprite_path):
            item_icon = pygame.image.load(sprite_path).convert_alpha()
            item_icon = pygame.transform.scale(item_icon, (item_icon.get_width() * 2, item_icon.get_height() * 2))
            icon_x = self.ICON_BOX_POS[0] + (self.ICON_BOX_SIZE[0] - item_icon.get_width()) // 2
            icon_y = self.ICON_BOX_POS[1] + (self.ICON_BOX_SIZE[1] - item_icon.get_height()) // 2
            screen.blit(item_icon, (icon_x, icon_y))
        else:
            fallback_icon = pygame.Surface((32, 32))
            fallback_icon.fill((150, 150, 150))
            screen.blit(fallback_icon, self.ICON_BOX_POS)

        # Description
        effect = get_item_effect(selected_item["name"]) or "Pas de description disponible."
        self.draw_multiline_text(screen, effect, self.DESCRIPTION_X, self.DESCRIPTION_Y, 462)

    def draw_multiline_text(self, screen, text, start_x, start_y, max_width):
        words = text.split()
        current_line = ""
        y_offset = 0

        for word in words:
            test_line = current_line + word + " "
            rendered = self.font_description.render(test_line, True, (255, 255, 255))
            if rendered.get_width() > max_width:
                rendered_line = self.font_description.render(current_line.strip(), True, (255, 255, 255))
                screen.blit(rendered_line, (start_x, start_y + y_offset))
                y_offset += rendered_line.get_height() + 5
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            rendered_line = self.font_description.render(current_line.strip(), True, (255, 255, 255))
            screen.blit(rendered_line, (start_x, start_y + y_offset))
