import pygame
import os
import unicodedata

# Chemins
ASSETS = os.path.join("assets", "ui", "party")
ICONS = os.path.join(ASSETS, "pokemon_icons")
FONTS = os.path.join("assets", "fonts")

CANCEL_POS = (398, 329)
DIALOGUE_BOX_POS = (2, 322)
DIALOGUE_BOX_SEL = (350, 258)

class PokemonMenu:
    def __init__(self, team):
        self.team = team
        self.selected_index = 0
        self.selection_active = False
        self.selected_option = 0
        self.closed = False


        self.font_bold = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 24)
        self.font_niv = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 22)
        self.font_dialogue = pygame.font.Font(os.path.join(FONTS, "power clear.ttf"), 25)

        self.images = self.load_images()
        self.icon_frames = [
            self.load_icon(p["name"]) for p in self.team
        ]
        self.frame_index = 0
        self.animation_timer = 0
        self.ANIMATION_DELAY = 400

        self.slot_positions = [
            (0, 0), (255, 15),
            (0, 95), (255, 110),
            (0, 190), (255, 205)
        ][:len(team)]  # Ne conserve que le nombre nécessaire de slots
        self.cancel_index = len(team)

        self.bg = pygame.image.load(os.path.join(ASSETS, "bg.png")).convert()

    def remove_accents(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def load_images(self):
        return {
            "round": pygame.image.load(os.path.join(ASSETS, "slot_round.png")).convert_alpha(),
            "round_selected": pygame.image.load(os.path.join(ASSETS, "slot_round_selected.png")).convert_alpha(),
            "square": pygame.image.load(os.path.join(ASSETS, "slot_square.png")).convert_alpha(),
            "square_selected": pygame.image.load(os.path.join(ASSETS, "slot_square_selected.png")).convert_alpha(),
            "open": pygame.image.load(os.path.join(ASSETS, "pokeball_open.png")).convert_alpha(),
            "close": pygame.image.load(os.path.join(ASSETS, "pokeball_close.png")).convert_alpha(),
            "hp_empty": pygame.image.load(os.path.join(ASSETS, "hp_bar_empty.png")).convert_alpha(),
            "cancel": pygame.image.load(os.path.join(ASSETS, "cancel.png")).convert_alpha(),
            "cancel_sel": pygame.image.load(os.path.join(ASSETS, "cancel_sel.png")).convert_alpha(),
            "dialogue_box": pygame.image.load(os.path.join(ASSETS, "dialogue_box.png")).convert_alpha(),
            "dialogue_box_enter": pygame.image.load(os.path.join(ASSETS, "dialogue_box_enter.png")).convert_alpha(),
            "dialogue_box_selection": pygame.image.load(os.path.join(ASSETS, "dialogue_box_selection.png")).convert_alpha()
        }

    def load_icon(self, name):
        clean_name = self.remove_accents(name).upper()
        path = os.path.join(ICONS, f"{clean_name}.png")
        if not os.path.exists(path):
            return []
        img = pygame.image.load(path).convert_alpha()
        fw, fh = img.get_width() // 2, img.get_height()
        return [img.subsurface((0, 0, fw, fh)), img.subsurface((fw, 0, fw, fh))]


    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.ANIMATION_DELAY:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 2

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if not self.selection_active:
            # Navigation dans les slots
            if event.key == pygame.K_UP and self.selected_index >= 2:
                self.selected_index -= 2

            elif event.key == pygame.K_DOWN:
                if self.selected_index + 2 < self.cancel_index:
                    self.selected_index += 2
                else:
                    self.selected_index = self.cancel_index  # Aller sur Cancel

            elif event.key == pygame.K_LEFT and self.selected_index % 2 == 1:
                self.selected_index -= 1

            elif event.key == pygame.K_RIGHT and self.selected_index % 2 == 0 and self.selected_index + 1 < self.cancel_index:
                self.selected_index += 1

            elif event.key == pygame.K_RETURN:
                if self.selected_index == self.cancel_index:
                    self.closed = True  # Ferme complètement le menu
                elif self.selected_index < len(self.team):
                    self.selection_active = True  # Ouvre le sous-menu

            # Escape n’a aucun effet ici

        else:
            # Navigation dans les options du sous-menu
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % 3

            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % 3

            elif event.key == pygame.K_RETURN:
                if self.selected_option == 2:  # "Annuler"
                    self.selection_active = False  # Revenir à l’écran de base

            # Escape n’a aucun effet ici non plus

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        for i, pos in enumerate(self.slot_positions):
            self.draw_slot(surface, i, pos)

        if not self.selection_active:
            self.draw_cancel(surface)
            self.draw_dialogue(surface, "Choisissez un Pokémon.")
        else:
            self.draw_selection(surface)

    def draw_slot(self, surface, index, base_pos):
        pokemon = self.team[index]
        name = pokemon["name"]
        level = pokemon.get("level", 5)
        current_hp = pokemon.get("hp", pokemon.get("stats", {}).get("hp", 20))
        max_hp = pokemon.get("stats", {}).get("hp", 20)
        gender = pokemon.get("gender", "male")

        x, y = base_pos
        pokeball_pos = (x + 10, y)
        hp_bar_pos = (x + 96, y + 50)
        hp_fill_pos = (x + 128, y + 52)
        name_pos = (x + 96, y + 22)
        level_pos = (x + 20, y + 68)
        hp_text_pos = (x + 158, y + 66)
        gender_pos = (x + 224, y + 22)
        icon_pos = (x + 40, y - 5)

        slot_img = (
            self.images["round_selected"] if index == 0 and index == self.selected_index else
            self.images["round"] if index == 0 else
            self.images["square_selected"] if index == self.selected_index else
            self.images["square"]
        )
        surface.blit(slot_img, (x, y))
        pokeball = self.images["open"] if index == self.selected_index else self.images["close"]
        surface.blit(pokeball, pokeball_pos)

        if self.icon_frames and index < len(self.icon_frames):
            surface.blit(self.icon_frames[index][self.frame_index], icon_pos)

        surface.blit(self.images["hp_empty"], hp_bar_pos)
        self.draw_health_bar(surface, hp_fill_pos, (96, 8), current_hp, max_hp)

        self.blit_text(surface, name, self.font_bold, name_pos)
        self.blit_text(surface, f"N. {level}", self.font_niv, level_pos)
        self.blit_text(surface, f"{current_hp}/{max_hp}", self.font_bold, hp_text_pos)

        gender_symbol = "♂" if gender == "male" else "♀"
        gender_color = (72, 104, 168) if gender == "male" else (240, 88, 152)
        self.blit_text(surface, gender_symbol, self.font_bold, gender_pos, gender_color)

    def draw_health_bar(self, surface, pos, size, hp, max_hp):
        ratio = max(0, min(1, hp / max_hp))
        fill = int(size[0] * ratio)
        color = (0, 192, 0) if ratio > 0.5 else (232, 192, 0) if ratio > 0.2 else (240, 64, 48)
        pygame.draw.rect(surface, color, pygame.Rect(pos[0], pos[1], fill, size[1]))

    def draw_cancel(self, surface):
        img = self.images["cancel_sel"] if self.selected_index == self.cancel_index else self.images["cancel"]
        surface.blit(img, CANCEL_POS)
        text = "RETOUR"
        center = (CANCEL_POS[0] + img.get_width() // 2, CANCEL_POS[1] + img.get_height() // 2)
        rect = self.font_bold.render(text, True, (248, 248, 248)).get_rect(center=center)
        self.blit_text(surface, text, self.font_bold, rect.topleft)

    def draw_dialogue(self, surface, text):
        surface.blit(self.images["dialogue_box"], DIALOGUE_BOX_POS)
        self.blit_text(surface, text, self.font_dialogue, (DIALOGUE_BOX_POS[0] + 16, DIALOGUE_BOX_POS[1] + 19), (88, 88, 80), (168, 184, 184))

    def draw_selection(self, surface):
        surface.blit(self.images["dialogue_box_enter"], DIALOGUE_BOX_POS)
        name = self.team[self.selected_index]["name"]
        self.blit_text(surface, f"Que faire avec {name} ?", self.font_dialogue, (DIALOGUE_BOX_POS[0] + 16, DIALOGUE_BOX_POS[1] + 19), (88, 88, 80), (168, 184, 184))
        surface.blit(self.images["dialogue_box_selection"], DIALOGUE_BOX_SEL)

        options = ["Envoyer", "Résumé", "Annuler"]
        for i, label in enumerate(options):
            pos = (DIALOGUE_BOX_SEL[0] + 24, DIALOGUE_BOX_SEL[1] + 18 + i * 32)
            text_surface = self.font_dialogue.render(label, True, (88, 88, 80))
            center_y = pos[1] + text_surface.get_height() // 2
            self.blit_text(surface, label, self.font_dialogue, pos, (88, 88, 80), (168, 184, 184))
            if i == self.selected_option:
                pygame.draw.polygon(surface, (88, 88, 80), [
                    (pos[0] - 11, center_y - 4),
                    (pos[0] - 11, center_y + 4),
                    (pos[0] - 3 , center_y)
                ])

    def blit_text(self, surface, text, font, pos, text_color=(248, 248, 248), shadow_color=(40, 40, 40)):
        shadow = font.render(text, True, shadow_color)
        text_render = font.render(text, True, text_color)
        surface.blit(shadow, (pos[0] + 2, pos[1] + 2))
        surface.blit(text_render, pos)
