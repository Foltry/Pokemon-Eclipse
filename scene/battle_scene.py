# scene/battle_scene.py

import pygame
from ui.battle_ui import BattleButton, BattleDialogBox, load_battle_ui

class BattleScene:
    def __init__(self):
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.selected_index = 0

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.selected_index in [1, 3]:
                    self.selected_index -= 1
            elif event.key == pygame.K_DOWN:
                if self.selected_index in [0, 2]:
                    self.selected_index += 1
            elif event.key == pygame.K_LEFT:
                if self.selected_index in [2, 3]:
                    self.selected_index -= 2
            elif event.key == pygame.K_RIGHT:
                if self.selected_index in [0, 1]:
                    self.selected_index += 2



    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        self.dialog_box.draw(screen, "Que doit faire Pikachu ?")

        # Dessiner tous les boutons sauf le sélectionné
        for i, button in enumerate(self.buttons):
            if i != self.selected_index:
                button.draw(screen, selected=False)

        # Dessiner le bouton sélectionné en dernier
        self.buttons[self.selected_index].draw(screen, selected=True)

