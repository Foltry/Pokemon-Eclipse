import unicodedata
import pygame
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

ASSETS = os.path.join("assets", "ui", "party")
ICONS = os.path.join(ASSETS, "pokemon_icons")
FONTS = os.path.join("assets", "fonts")

CANCEL_POS = (398, 329)
DIALOGUE_BOX_POS = (2, 322)
DIALOGUE_BOX_SEL = (350, 258)

def normalize_name(name):
    return unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8").upper()

class PokemonMenu:
    def __init__(self, team, current_ally_id, surface=None):
        self.team = team
        self.current_ally_id = current_ally_id
        self.surface = surface

        # État interne
        self.selected_index = 0
        self.selection_active = False
        self.selected_option = 0
        self.closed = False
        self.override_text = None
        self.option_chosen = None

        # Fonts
        self.font_bold = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 24)
        self.font_niv = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 22)
        self.font_dialogue = pygame.font.Font(os.path.join(FONTS, "power clear.ttf"), 25)

        # Images
        self.images = self.load_images()
        self.bg = pygame.image.load(os.path.join(ASSETS, "bg.png")).convert()
        self.icon_frames = [self.load_icon(p["name"]) for p in team]

        # Animation
        self.frame_index = 0
        self.animation_timer = 0
        self.ANIMATION_DELAY = 400

        # Position slots
        self.slot_positions = [
            (0, 0), (255, 15),
            (0, 95), (255, 110),
            (0, 190), (255, 205)
        ][:len(team)]
        self.cancel_index = len(team)

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
            "dialogue_box_selection": pygame.image.load(os.path.join(ASSETS, "dialogue_box_selection.png")).convert_alpha(),
        }

    def load_icon(self, name):
        path = os.path.join(ICONS, f"{normalize_name(name)}.png")
        if not os.path.exists(path):
            return []
        img = pygame.image.load(path).convert_alpha()
        w = img.get_width() // 2
        return [img.subsurface((0, 0, w, img.get_height())), img.subsurface((w, 0, w, img.get_height()))]

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.ANIMATION_DELAY:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        if self.override_text and not self.selection_active:
            self.override_text = None

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        self.option_chosen = None

        if self.selection_active:
            self.handle_selection_input(event)
        else:
            self.handle_slot_navigation(event)

    def handle_selection_input(self, event):
        if event.key in (pygame.K_UP, pygame.K_z):
            self.selected_option = (self.selected_option - 1) % 2
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_option = (self.selected_option + 1) % 2
        elif event.key == pygame.K_RETURN:
            selected_pkm = self.team[self.selected_index]
            if self.selected_option == 0:  # Envoyer
                if selected_pkm["id"] == self.current_ally_id:
                    self.override_text = f"{selected_pkm['name']} est déjà au combat."
                else:
                    self.option_chosen = "send"
                    self.closed = True
            elif self.selected_option == 1:  # Annuler
                self.selection_active = False

    def handle_slot_navigation(self, event):
        if event.key in (pygame.K_UP, pygame.K_z):
            if self.selected_index == self.cancel_index:
                self.selected_index = len(self.team) - 1 if len(self.team) % 2 == 1 else len(self.team) - 2
            elif self.selected_index >= 2:
                self.selected_index -= 2
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if self.selected_index + 2 < self.cancel_index:
                self.selected_index += 2
            else:
                self.selected_index = self.cancel_index
        elif event.key in (pygame.K_LEFT, pygame.K_q):
            if self.selected_index % 2 == 1:
                self.selected_index -= 1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if self.selected_index % 2 == 0 and self.selected_index + 1 < self.cancel_index:
                self.selected_index += 1
        elif event.key == pygame.K_RETURN:
            if self.selected_index == self.cancel_index:
                self.closed = True
            else:
                self.selection_active = True

    def draw(self, surface=None):
        if surface is None:
            surface = self.surface
        if surface is None:
            return

        surface.blit(self.bg, (0, 0))
        for i, pos in enumerate(self.slot_positions):
            self.draw_slot(surface, i, pos)

        if not self.selection_active:
            self.draw_cancel(surface)

        self.draw_dialogue(surface)

    def draw_slot(self, surface, index, pos):
        p = self.team[index]
        stats = p.get("stats") or p.get("base_stats", {})
        hp, max_hp = p.get("hp", stats["hp"]), stats["hp"]

        slot_img = (
            self.images["round_selected"] if index == 0 and index == self.selected_index else
            self.images["round"] if index == 0 else
            self.images["square_selected"] if index == self.selected_index else
            self.images["square"]
        )
        surface.blit(slot_img, pos)
        surface.blit(self.images["open" if index == self.selected_index else "close"], (pos[0] + 10, pos[1]))

        if self.icon_frames[index]:
            surface.blit(self.icon_frames[index][self.frame_index], (pos[0] + 40, pos[1] - 5))

        surface.blit(self.images["hp_empty"], (pos[0] + 96, pos[1] + 50))
        self.draw_health_bar(surface, (pos[0] + 128, pos[1] + 52), (96, 8), hp, max_hp)

        self.blit_text(surface, p["name"], self.font_bold, (pos[0] + 96, pos[1] + 22))
        self.blit_text(surface, f"N. {p['level']}", self.font_niv, (pos[0] + 20, pos[1] + 68))
        self.blit_text(surface, f"{hp}/{max_hp}", self.font_bold, (pos[0] + 158, pos[1] + 66))

        gender_symbol = "♂" if p.get("gender") == "male" else "♀"
        gender_color = (72, 104, 168) if gender_symbol == "♂" else (240, 88, 152)
        self.blit_text(surface, gender_symbol, self.font_bold, (pos[0] + 224, pos[1] + 22), gender_color)

    def draw_cancel(self, surface):
        img = self.images["cancel_sel"] if self.selected_index == self.cancel_index else self.images["cancel"]
        surface.blit(img, CANCEL_POS)
        rect = self.font_bold.render("RETOUR", True, (248, 248, 248)).get_rect(center=(CANCEL_POS[0]+img.get_width()//2, CANCEL_POS[1]+img.get_height()//2))
        self.blit_text(surface, "RETOUR", self.font_bold, rect.topleft)

    def draw_dialogue(self, surface):
        box = self.images["dialogue_box_enter"] if self.selection_active else self.images["dialogue_box"]
        surface.blit(box, DIALOGUE_BOX_POS)

        text = self.override_text or "Choisissez un Pokémon."
        self.blit_text(surface, text, self.font_dialogue, (DIALOGUE_BOX_POS[0] + 16, DIALOGUE_BOX_POS[1] + 19),
                       text_color=(88, 88, 80), shadow_color=(168, 184, 184))

        if self.selection_active:
            surface.blit(self.images["dialogue_box_selection"], DIALOGUE_BOX_SEL)
            options = ["Envoyer", "Annuler"]
            for i, label in enumerate(options):
                x, y = DIALOGUE_BOX_SEL[0] + 24, DIALOGUE_BOX_SEL[1] + 18 + i * 32
                self.blit_text(surface, label, self.font_dialogue, (x, y), (88, 88, 80), (168, 184, 184))
                if i == self.selected_option:
                    pygame.draw.polygon(surface, (88, 88, 80), [(x - 11, y + 10), (x - 11, y + 18), (x - 3, y + 14)])

    def draw_health_bar(self, surface, pos, size, hp, max_hp):
        ratio = max(0, min(1, hp / max_hp))
        fill = int(size[0] * ratio)
        color = (0, 192, 0) if ratio > 0.5 else (232, 192, 0) if ratio > 0.2 else (240, 64, 48)
        pygame.draw.rect(surface, color, pygame.Rect(pos[0], pos[1], fill, size[1]))

    def blit_text(self, surface, text, font, pos, text_color=(248, 248, 248), shadow_color=(40, 40, 40)):
        shadow = font.render(text, True, shadow_color)
        surface.blit(shadow, (pos[0] + 2, pos[1] + 2))
        surface.blit(font.render(text, True, text_color), pos)

    def get_selected_pokemon(self):
        return self.team[self.selected_index]
