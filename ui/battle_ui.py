# ui/battle_ui.py

import os
import pygame
import gif_pygame
from PIL import Image
from ui.health_bar import HealthBar
from ui.xp_bar import XPBar
from data.pokemon_loader import get_pokemon_by_id

ASSETS = os.path.join("assets", "ui", "battle")
FONTS = os.path.join("assets", "fonts")
SPRITE_DIR = os.path.join("assets", "sprites", "pokemon")
CMD_IMG = pygame.image.load(os.path.join(ASSETS, "cursor_command.png"))

BUTTON_WIDTH = 130
BUTTON_HEIGHT = 46

def get_gif_max_size(gif_path):
    try:
        with Image.open(gif_path) as img:
            max_width, max_height = 0, 0
            for frame in range(img.n_frames):
                img.seek(frame)
                w, h = img.size
                max_width = max(max_width, w)
                max_height = max(max_height, h)
            return int(max_width * 2), int(max_height * 2)
    except Exception:
        return 192, 192

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
        self.font = pygame.font.Font(os.path.join(FONTS, "power clear.ttf"), 25)
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

    def draw(self, surface, text, offset_x=0, offset_y=0, draw_box=True):
        if draw_box:
            surface.blit(self.image, self.rect.topleft)
        lines = self.wrap_text(text)
        y = self.rect.top + self.margin_y + offset_y
        for line in lines:
            txt_surface = self.font.render(line, True, self.text_color)
            surface.blit(txt_surface, (self.rect.left + self.margin_x + offset_x, y))
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

    ally = get_pokemon_by_id(ally_id)
    enemy = get_pokemon_by_id(enemy_id)

    ally_path = os.path.join(SPRITE_DIR, ally["sprites"]["back"])
    enemy_path = os.path.join(SPRITE_DIR, enemy["sprites"]["front"])

    ally_size = get_gif_max_size(ally_path)
    enemy_size = get_gif_max_size(enemy_path)

    ally_sprite = resize_gif(gif_pygame.load(ally_path), ally_size)
    enemy_sprite = resize_gif(gif_pygame.load(enemy_path), enemy_size)

    # === Base positions ===
    base_ally_rect = base_ally.get_rect(topleft=(-128, 240))
    base_enemy_rect = base_enemy.get_rect(topleft=(255, 115))

    ally_x = base_ally_rect.centerx - (ally_sprite.get_width() // 2)
    ally_y = base_ally_rect.centery - ally_sprite.get_height() + 30

    enemy_x = base_enemy_rect.centerx - (enemy_sprite.get_width() // 2) - 5
    enemy_y = base_enemy_rect.centery - enemy_sprite.get_height()

    return (base_ally, base_enemy), (ally_sprite, enemy_sprite), ((ally_x, ally_y), (enemy_x, enemy_y))

def draw_combat_scene(
    screen,
    background,
    bases,
    sprites,
    positions,
    ally_name="",
    enemy_name="",
    ally_hp=100,
    ally_max_hp=100,
    enemy_hp=100,
    enemy_max_hp=100,
    ally_level=5,
    enemy_level=5,
    enemy_gender="?",
    ally_xp=0,
    ally_max_xp=100
):
    load_status_images()
    font_pkm = pygame.font.Font(os.path.join(FONTS, "power clear.ttf"), 27)
    font_pv = pygame.font.Font(os.path.join(FONTS, "power clear bold.ttf"), 27)

    screen.blit(background, (0, 0))

    base_ally, base_enemy = bases
    ally_sprite, enemy_sprite = sprites
    ally_pos, enemy_pos = positions

    screen.blit(base_ally, (-128, 240))
    screen.blit(base_enemy, (255, 115))

    screen.blit(ally_sprite.blit_ready(), ally_pos)
    if enemy_sprite:
        screen.blit(enemy_sprite.blit_ready(), enemy_pos)

    screen.blit(STATUS_PLAYER, (268, 193))
    screen.blit(STATUS_ENEMY, (0, 35))

    enemy_name_text = font_pkm.render(enemy_name, True, (0, 0, 0))
    gender_color = (66, 150, 255) if enemy_gender == "♂" else (255, 105, 180) if enemy_gender == "♀" else (120, 120, 120)
    enemy_gender_text = font_pv.render(enemy_gender, True, gender_color)
    enemy_level_text = font_pv.render(f"Nv.{enemy_level}", True, (51, 51, 51))

    screen.blit(enemy_name_text, (10, 45))
    screen.blit(enemy_gender_text, (120, 45))
    screen.blit(enemy_level_text, (140, 45))

    ally_name_text = font_pkm.render(ally_name, True, (0, 0, 0))
    ally_level_text = font_pv.render(f"Nv.{ally_level}", True, (51, 51, 51))

    screen.blit(ally_name_text, (305, 205))
    screen.blit(ally_level_text, (430, 205))

    ally_bar = HealthBar((402, 232), (98, 9), ally_max_hp)
    ally_bar.update(ally_hp)
    ally_bar.draw(screen)

    enemy_bar = HealthBar((116, 73), (98, 9), enemy_max_hp)
    enemy_bar.update(enemy_hp)
    enemy_bar.draw(screen)

    hp_text = font_pv.render(f"{ally_hp}/{ally_max_hp}", True, (51, 51, 51))
    hp_text = pygame.transform.scale(hp_text, (hp_text.get_width(), int(hp_text.get_height() * 0.65)))
    screen.blit(hp_text, (410, 246))

    xp_bar = XPBar((308, 267), ally_max_xp)
    xp_bar.update(ally_xp)
    xp_bar.draw(screen)
