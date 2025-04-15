# ui/battle_ui.py

import pygame
import os

ASSETS = os.path.join("assets", "ui", "battle")
CMD_IMG = pygame.image.load(os.path.join(ASSETS, "cursor_command.png"))

BUTTON_WIDTH = 130
BUTTON_HEIGHT = 46

def get_command_button(index):
    """
    Récupère le bouton et sa version sélectionnée depuis la sprite sheet
    """
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
    def __init__(self, pos=(0 , 288)):
        self.image = pygame.image.load(os.path.join(ASSETS, "dialogue_box.png"))
        self.rect = self.image.get_rect(topleft=pos)
        self.font = pygame.font.SysFont("Arial", 20)
        

    def draw(self, surface, text):
        surface.blit(self.image, self.rect.topleft)
        txt_surface = self.font.render(text, True, (0, 0, 0))
        surface.blit(txt_surface, (self.rect.left + 21, self.rect.top + 20))

def load_battle_ui():
    bg = pygame.image.load(os.path.join(ASSETS, "battle_bg.png")).convert()
    
    dialog = BattleDialogBox()

    # Positionnement 2x2 des boutons dans le coin inférieur droit
    buttons = [
        BattleButton(0, (250, 294)),     # Fight
        BattleButton(1, (250, 336)),   # Pokémon
        BattleButton(2, (376, 294)),     # Bag
        BattleButton(3, (376, 336))    # Run
    ]
    return bg, dialog, buttons
