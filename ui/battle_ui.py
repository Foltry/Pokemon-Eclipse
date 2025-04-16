import os
import pygame
import gif_pygame
from ui.health_bar import HealthBar

# === PATHS & CONST ===
ASSETS = os.path.join("assets", "ui", "battle")
FONTS = os.path.join("assets", "fonts")
CMD_IMG = pygame.image.load(os.path.join(ASSETS, "cursor_command.png"))

BUTTON_WIDTH = 130
BUTTON_HEIGHT = 46
ALLY_SPRITE_SIZE = (160, 160)
ENEMY_SPRITE_SIZE = (96, 96)

# === UI ELEMENTS ===

def get_command_button(index):
    normal = CMD_IMG.subsurface(pygame.Rect(0, index * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT))
    selected = CMD_IMG.subsurface(pygame.Rect(BUTTON_WIDTH, index * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT))
    return normal, selected

class BattleButton:
    def __init__(self, index, pos):
        self.normal, self.selected = get_command_button(index)
        self.rect = self.normal.get_rect(topleft=pos)

    def draw(self, surface, selected=False):
        surface.blit(self.selected if selected else self.normal, self.rect.topleft)

class BattleDialogBox:
    def __init__(self, pos=(0, 288)):
        self.image = pygame.image.load(os.path.join(ASSETS, "dialogue_box.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        font_path = os.path.join(FONTS, "power clear.ttf")
        self.font = pygame.font.Font(font_path, 25)

        self.text_color = (0, 0, 0)
        self.margin_x = 22
        self.margin_y = 25
        self.line_spacing = 2
        self.max_width = 216

    def wrap_text(self, text):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= self.max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def draw(self, surface, text):
        surface.blit(self.image, self.rect.topleft)
        lines = self.wrap_text(text)
        y = self.rect.top + self.margin_y

        for line in lines:
            txt_surface = self.font.render(line, True, self.text_color)
            surface.blit(txt_surface, (self.rect.left + self.margin_x, y))
            y += txt_surface.get_height() + self.line_spacing

def load_battle_ui():
    bg = pygame.image.load(os.path.join(ASSETS, "battle_bg.png")).convert()
    dialog = BattleDialogBox()
    buttons = [
        BattleButton(0, (250, 294)),
        BattleButton(1, (250, 336)),
        BattleButton(2, (376, 294)),
        BattleButton(3, (376, 336))
    ]
    return bg, dialog, buttons

# === SPRITES & STATUS UI ===

STATUS_PLAYER = None
STATUS_ENEMY = None
_status_loaded = False

def load_status_images():
    global STATUS_PLAYER, STATUS_ENEMY, _status_loaded
    if not _status_loaded:
        STATUS_PLAYER = pygame.image.load(os.path.join(ASSETS, "status_player.png")).convert_alpha()
        STATUS_ENEMY = pygame.image.load(os.path.join(ASSETS, "status_enemy.png")).convert_alpha()
        _status_loaded = True

def resize_gif(gif_obj, size):
    resized_frames = [
        (pygame.transform.scale(frame, size), duration)
        for frame, duration in gif_obj.get_datas()
    ]
    return gif_pygame.GIFPygame(resized_frames)

def load_combat_sprites(ally_id, enemy_id):
    base_ally = pygame.image.load(os.path.join(ASSETS, "base_ally.png")).convert_alpha()
    base_enemy = pygame.image.load(os.path.join(ASSETS, "base_enemy.png")).convert_alpha()

    path_back = os.path.join("assets", "sprites", "pokemon", "back", f"{ally_id}.gif")
    path_front = os.path.join("assets", "sprites", "pokemon", "front", f"{enemy_id}.gif")

    ally_sprite = gif_pygame.load(path_back)
    enemy_sprite = gif_pygame.load(path_front)

    ally_sprite = resize_gif(ally_sprite, ALLY_SPRITE_SIZE)
    enemy_sprite = resize_gif(enemy_sprite, ENEMY_SPRITE_SIZE)

    return (base_ally, base_enemy), (ally_sprite, enemy_sprite)

def draw_combat_scene(
    screen,
    background,
    bases,
    sprites,
    ally_name="",
    enemy_name="",
    ally_hp=100,
    ally_max_hp=100,
    enemy_hp=100,
    enemy_max_hp=100
):
    load_status_images()
    font_pkm = pygame.font.Font(os.path.join(FONTS, "power clear.ttf"), 27)
    font_pv = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 27)

    screen.blit(background, (0, 0))

    base_ally, base_enemy = bases
    ally_sprite, enemy_sprite = sprites

    # Sol
    screen.blit(base_ally, (-128, 240))
    screen.blit(base_enemy, (255, 115))

    # Sprites
    screen.blit(ally_sprite.blit_ready(), (40, 160))
    screen.blit(enemy_sprite.blit_ready(), (340, 90))

    # Status boxes
    screen.blit(STATUS_PLAYER, (268, 193))
    screen.blit(STATUS_ENEMY, (0, 35))

    # Noms des Pokémon
    text_ally = font_pkm.render(ally_name, True, (0, 0, 0))
    text_enemy = font_pkm.render(enemy_name, True, (0, 0, 0))
    screen.blit(text_ally, (305, 205))
    screen.blit(text_enemy, (10, 45))

    # Barres de vie
    ally_bar = HealthBar((402, 232), (98, 9), ally_max_hp)
    ally_bar.update(ally_hp)
    ally_bar.draw(screen)

    enemy_bar = HealthBar((116, 73), (98, 9), enemy_max_hp)
    enemy_bar.update(enemy_hp)
    enemy_bar.draw(screen)

    # PV texte du joueur (gris)
# PV texte du joueur (sous la barre de vie)
    hp_text = font_pv.render(f"{ally_hp}/{ally_max_hp}", True, (51, 51, 51))
    hp_text = pygame.transform.scale(hp_text, (hp_text.get_width(), int(hp_text.get_height() * 0.65)))
    screen.blit(hp_text, (410, 246))

