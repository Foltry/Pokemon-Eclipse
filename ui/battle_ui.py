import os
import pygame
import gif_pygame

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
        self.margin_x = 22  # Ce qui donne x=19 pour le texte
        self.margin_y = 25  # Ce qui donne y=335 (288 + 47)
        self.line_spacing = 2
        self.max_width = 216  # Largeur utile max pour le texte

    def wrap_text(self, text):
        """Retour à la ligne automatique dans la zone max_width."""
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

# === SPRITE HANDLING ===

def resize_gif(gif_obj, size):
    resized_frames = [
        (pygame.transform.scale(frame, size), duration)
        for frame, duration in gif_obj.get_datas()
    ]
    return gif_pygame.GIFPygame(resized_frames)

def load_combat_sprites(ally_id, enemy_id):
    base_ally = pygame.image.load(os.path.join(ASSETS, "base_ally.png")).convert_alpha()
    base_enemy = pygame.image.load(os.path.join(ASSETS, "base_enemy.png")).convert_alpha()

    path_back = os.path.join("assets", "sprites", "pokemon", "back", f"{ally_id:03}.gif")
    path_front = os.path.join("assets", "sprites", "pokemon", "front", f"{enemy_id:03}.gif")

    ally_sprite = gif_pygame.load(path_back)
    enemy_sprite = gif_pygame.load(path_front)

    if ally_sprite is None:
        raise FileNotFoundError(f"❌ Sprite dos introuvable ou invalide : {path_back}")
    if enemy_sprite is None:
        raise FileNotFoundError(f"❌ Sprite face introuvable ou invalide : {path_front}")

    ally_sprite = resize_gif(ally_sprite, ALLY_SPRITE_SIZE)
    enemy_sprite = resize_gif(enemy_sprite, ENEMY_SPRITE_SIZE)

    return (base_ally, base_enemy), (ally_sprite, enemy_sprite)

def draw_combat_scene(screen, background, bases, sprites):
    screen.blit(background, (0, 0))

    base_ally, base_enemy = bases
    ally_sprite, enemy_sprite = sprites

    screen.blit(base_ally, (-128, 240))      # Sol du joueur
    screen.blit(base_enemy, (255, 115))      # Sol de l’ennemi

    screen.blit(ally_sprite.blit_ready(), (40, 160))    # Dos joueur
    screen.blit(enemy_sprite.blit_ready(), (340, 90))   # Face ennemi
