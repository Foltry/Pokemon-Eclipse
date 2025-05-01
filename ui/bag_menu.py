# ui/bag_menu.py

import pygame
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.items_loader import get_item_sprite, get_item_effect, get_item_category
from battle.use_item import use_item_on_pokemon
from battle.capture_handler import attempt_capture
from core import config
from core.run_manager import run_manager

class BagMenu:
    def __init__(self, inventory):
        self.empty_mode = not inventory
        if self.empty_mode:
            self.inventory = [{"name": "FERMER LE SAC", "quantity": 0}]
        else:
            self.inventory = inventory

        self.selected_index = 0
        self.scroll_offset = 0
        self.message_queue = []

        self.background = self.load_image("assets/ui/Bag/bg_items.png", (0, 0, 0))
        self.cursor_img = self.load_image("assets/ui/Bag/cursor.png", (255, 0, 0))
        self.bag_item_img = self.load_image("assets/ui/Bag/bag_items.png", (100, 100, 255))

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

    def queue_message(self, text):
        self.message_queue.append(text)

    def handle_event(self, event, scene_manager):
        if event.type == pygame.KEYDOWN:
            if self.message_queue:
                if event.key == pygame.K_RETURN:
                    self.message_queue.pop(0)
                return

            # === Touche ÉCHAP : revenir à la scène précédente ===
            if event.key == pygame.K_ESCAPE:
                scene_manager.go_back()
                return

            # === Navigation dans l'inventaire ===
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

            # === Utilisation d’un objet ===
            elif event.key == pygame.K_RETURN:
                if self.empty_mode:
                    scene_manager.go_back()
                    return

                selected_item = self.inventory[self.selected_index]
                item_name = selected_item["name"]

                if item_name == "FERMER LE SAC":
                    scene_manager.go_back()
                    return

                category = get_item_category(item_name)

                # === Utilisation d’une Ball ===
                if category == "standard-balls":
                    current_scene = scene_manager.scene_stack[-2] if len(scene_manager.scene_stack) > 1 else None
                    if current_scene:
                        current_scene.throw_ball(item_name)
                        selected_item["quantity"] -= 1
                        if selected_item["quantity"] <= 0:
                            self.inventory.pop(self.selected_index)
                    scene_manager.go_back()
                    return

                # === Sinon : objets type soins ===
                pokemon = run_manager.get_team()[0]
                result = use_item_on_pokemon(item_name, pokemon)
                self.queue_message(result["message"])

                if result["success"]:
                    selected_item["quantity"] -= 1
                    if selected_item["quantity"] <= 0:
                        self.inventory.pop(self.selected_index)


    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.bag_item_img, (30, 17))

        if self.message_queue:
            self.draw_message(screen)
            return

        for i in range(self.VISIBLE_ITEM_COUNT):
            item_index = self.scroll_offset + i
            if item_index >= len(self.inventory):
                break

            item = self.inventory[item_index]
            x = self.LIST_START_X
            y = self.LIST_START_Y + i * self.ITEM_SPACING_Y

            name_surface = self.font_items.render(item["name"], True, (0, 0, 0))
            screen.blit(name_surface, (x, y))

            if not (self.empty_mode or item["name"] == "FERMER LE SAC"):
                quantity_surface = self.font_items.render(f"x{item['quantity']}", True, (0, 0, 0))
                screen.blit(quantity_surface, (self.QUANTITY_X, y))

            if item_index == self.selected_index:
                cursor_rect = self.cursor_img.get_rect()
                cursor_pos = (x + self.CURSOR_OFFSET_X, y + (name_surface.get_height() - cursor_rect.height) // 2)
                screen.blit(self.cursor_img, cursor_pos)

        if not self.empty_mode and self.inventory[self.selected_index]["name"] != "FERMER LE SAC":
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

            effect = get_item_effect(selected_item["name"]) or "Pas de description disponible."
            self.draw_multiline_text(screen, effect, self.DESCRIPTION_X, self.DESCRIPTION_Y, 478 - self.DESCRIPTION_X)

    def draw_message(self, screen):
        """Affiche un message avec retour à la ligne depuis (91, 324), largeur max 387 px (jusqu’à x = 478)."""
        if not self.message_queue:
            return

        text = self.message_queue[0]
        font = self.font_description
        max_width = 387  # 478 - 91
        start_x = 91
        start_y = 324
        y_offset = 0
        words = text.split()
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] > max_width:
                rendered_line = font.render(current_line.strip(), True, (255, 255, 255))
                screen.blit(rendered_line, (start_x, start_y + y_offset))
                y_offset += rendered_line.get_height() + 5
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            rendered_line = font.render(current_line.strip(), True, (255, 255, 255))
            screen.blit(rendered_line, (start_x, start_y + y_offset))


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

# # === TEST rapide ===
# if __name__ == "__main__":

#     pygame.init()
#     screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
#     pygame.display.set_caption("Test BagMenu")

#     # === Simulation d’un Pokémon et d’un objet ===
#     run_manager.team = [{
#         "name": "Pikachu",
#         "level": 5,
#         "stats": {"hp": 10},  # HP actuels
#         "base_stats": {"hp": 35},  # HP max
#         "gender": "male"
#     }]
#     run_manager.items.clear()
#     run_manager.add_item("Potion", 1)

#     inventory = run_manager.get_items_as_inventory()
#     bag_menu = BagMenu(inventory)

#     class DummyManager:
#         def change_scene(self, scene):
#             print("[DEBUG TEST] Changement de scène :", scene)

#     clock = pygame.time.Clock()
#     running = True
#     print("[DEBUG TEST] Lancement test BagMenu. Appuyez sur Entrée pour utiliser la Potion.")

#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             else:
#                 bag_menu.handle_event(event, DummyManager())

#         screen.fill((0, 0, 0))
#         bag_menu.update(clock.tick(60))
#         bag_menu.draw(screen)
#         pygame.display.flip()

#     pygame.quit()
#     sys.exit()
