import pygame
import json
import random
from ui.battle_ui import (
    load_battle_ui,
    load_combat_sprites,
    draw_combat_scene
)
from core.scene_manager import Scene
from core.run_manager import run_manager

class BattleScene(Scene):
    def __init__(self):
        self.bg, self.dialog_box, self.buttons = load_battle_ui()

        self.button_grid = [
            [0, 1],
            [2, 3],
        ]
        self.grid_pos = [0, 0]
        self.selected_index = self.button_grid[0][0]

        # Pokémon du joueur
        starter = run_manager.get_team()[0]
        self.ally_id = starter["id"]
        self.ally_name = starter.get("name_fr", starter.get("name_en", "???"))
        self.ally_hp = self.ally_max_hp = starter["base_stats"]["hp"]
        self.ally_level = 5
        self.ally_xp = 30          # XP actuelle
        self.ally_max_xp = 100     # XP max avant passage de niveau

        # Pokémon ennemi temporaire
        self.enemy_id = "016"
        with open("data/pokemon.json", encoding="utf-8") as f:
            data = json.load(f)
            enemy = next((p for p in data if str(p["id"]).zfill(3) == self.enemy_id), None)
            if not enemy:
                raise ValueError(f"❌ Ennemi avec ID {self.enemy_id} introuvable.")
            
            self.enemy_name = enemy.get("name_fr", enemy.get("name", "Inconnu"))
            self.enemy_hp = self.enemy_max_hp = enemy.get("base_stats", {}).get("hp", 50)



        self.enemy_level = 5
        self.enemy_gender = random.choice(["♂", "♀"])

        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)

    def on_enter(self): pass
    def on_exit(self): pass
    def update(self, dt): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            col, row = self.grid_pos
            if event.key == pygame.K_UP and row > 0:
                row -= 1
            elif event.key == pygame.K_DOWN and row < 1:
                row += 1
            elif event.key == pygame.K_LEFT and col > 0:
                col -= 1
            elif event.key == pygame.K_RIGHT and col < 1:
                col += 1
            elif event.key == pygame.K_RETURN:
                self.selected_index = self.button_grid[col][row]
                print(f"[ACTION] Bouton {self.selected_index} sélectionné")

            self.grid_pos = [col, row]
            self.selected_index = self.button_grid[col][row]

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
            ally_level=self.ally_level,
            enemy_level=self.enemy_level,
            enemy_gender=self.enemy_gender,
            ally_xp=self.ally_xp,
            ally_max_xp=self.ally_max_xp
        )

        self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")

        for i, button in enumerate(self.buttons):
            if i != self.selected_index:
                button.draw(screen, selected=False)
        self.buttons[self.selected_index].draw(screen, selected=True)
