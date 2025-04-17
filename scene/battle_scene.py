import pygame
import json
from ui.battle_ui import (
    load_battle_ui,
    load_combat_sprites,
    draw_combat_scene
)
from core.scene_manager import Scene
import core.run_manager


class BattleScene(Scene):
    def __init__(self):
        # Chargement de l’UI de combat
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.selected_index = 0

        # Récupère le Pokémon choisi via run_manager
        starter = run_manager.get_team()[0]  # Le premier Pokémon de l’équipe
        self.ally_id = starter["id"]
        self.ally_name = starter["name"]
        self.ally_hp = self.ally_max_hp = starter["base_hp"]

        # Pokémon ennemi temporaire (ex: Roucool)
        self.enemy_id = "016"
        with open("data/pokemon.json", encoding="utf-8") as f:
            data = json.load(f)
            self.enemy_name = data[self.enemy_id]["name"]
            self.enemy_hp = self.enemy_max_hp = data[self.enemy_id]["base_hp"]

        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)

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
            elif event.key == pygame.K_RETURN:
                print(f"[ACTION] Bouton {self.selected_index} sélectionné")

    def draw(self, screen):
        draw_combat_scene(
            screen,
            self.bg,
            self.bases,
            self.sprites,
            ally_name=self.ally_name,
            enemy_name=self.enemy_name,
            ally_hp=self.ally_hp,
            ally_max_hp=self.ally_max_hp,
            enemy_hp=self.enemy_hp,
            enemy_max_hp=self.enemy_max_hp,
        )

        self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")

        for i, button in enumerate(self.buttons):
            if i != self.selected_index:
                button.draw(screen, selected=False)
        self.buttons[self.selected_index].draw(screen, selected=True)
