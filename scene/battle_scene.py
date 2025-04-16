import pygame
import json
from ui.battle_ui import (
    BattleButton,
    BattleDialogBox,
    load_battle_ui,
    load_combat_sprites,
    draw_combat_scene
)

class BattleScene:
    def __init__(self):
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.selected_index = 0

        # IDs utilisés avec zéros non significatifs (ex : "025", "016")
        self.ally_id = "025"
        self.enemy_id = "016"

        # Chargement des données Pokémon
        with open("data/pokemon.json", encoding="utf-8") as f:
            self.pokemon_data = json.load(f)

        # Noms dynamiques récupérés depuis le fichier
        self.ally_name = self.pokemon_data[self.ally_id]["name"]
        self.enemy_name = self.pokemon_data[self.enemy_id]["name"]

        # Chargement des assets visuels de combat
        self.bases, self.sprites = load_combat_sprites(
            ally_id=self.ally_id,
            enemy_id=self.enemy_id
        )

    def on_enter(self): pass
    def on_exit(self): pass

    def update(self, dt): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.selected_index in [1, 3]:
                self.selected_index -= 1
            elif event.key == pygame.K_DOWN and self.selected_index in [0, 2]:
                self.selected_index += 1
            elif event.key == pygame.K_LEFT and self.selected_index in [2, 3]:
                self.selected_index -= 2
            elif event.key == pygame.K_RIGHT and self.selected_index in [0, 1]:
                self.selected_index += 2

    def draw(self, screen):
        draw_combat_scene(screen, self.bg, self.bases, self.sprites, self.ally_name, self.enemy_name)
        self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")

        for i, button in enumerate(self.buttons):
            if i != self.selected_index:
                button.draw(screen, selected=False)
        self.buttons[self.selected_index].draw(screen, selected=True)
