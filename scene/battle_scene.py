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
from scene.bonus_scene import BonusScene

class BattleScene(Scene):
    def __init__(self):
        self.bg, self.dialog_box, self.buttons = load_battle_ui()

        self.button_grid = [[0, 1], [2, 3]]
        self.grid_pos = [0, 0]
        self.selected_index = self.button_grid[0][0]

        # Pokémon du joueur
        starter = run_manager.get_team()[0]
        self.ally_id = starter["id"]
        self.ally_name = starter.get("name_fr", starter.get("name", ""))
        self.ally_level = starter.get("level", 5)
        self.ally_hp = self.ally_max_hp = starter["base_stats"]["hp"]
        self.ally_xp = starter.get("xp", 0)
        self.ally_max_xp = 100  # temporaire

        # Pokémon ennemi
        self.enemy_id = 16
        self.enemy_level = 5
        self.enemy_gender = random.choice(["♂", "♀"])

        with open("data/pokemon.json", encoding="utf-8") as f:
            data = json.load(f)
            self.enemy_data = next(
                (p for p in data if int(p["id"]) == int(self.enemy_id)), None
            )

        if not self.enemy_data:
            raise ValueError(f"❌ Données manquantes pour le Pokémon #{self.enemy_id}")

        self.enemy_name = self.enemy_data.get("name_fr", self.enemy_data.get("name", "???"))
        self.enemy_hp = self.enemy_max_hp = self.enemy_data["stats"]["hp"]
        self.enemy_base_exp = self.enemy_data.get("base_experience", 50)

        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)
        self.victory_handled = False

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
                if self.selected_index == 0:
                    damage = random.randint(8, 12)
                    self.enemy_hp = max(0, self.enemy_hp - damage)
                    if self.enemy_hp == 0 and not self.victory_handled:
                        self.handle_victory()
                elif self.selected_index == 3:
                    print("Fuite !")
                    self.manager.change_scene(BonusScene())

            self.grid_pos = [col, row]
            self.selected_index = self.button_grid[col][row]

    def handle_victory(self):
        self.victory_handled = True
        exp = self.enemy_base_exp
        level = self.enemy_level
        xp_gain = int((exp * level) / 7)

        for poke in run_manager.get_team():
            poke["xp"] = poke.get("xp", 0) + xp_gain
            print(f"{poke.get('name_fr', poke.get('name'))} a gagné {xp_gain} XP ! (total: {poke['xp']})")

        self.manager.change_scene(BonusScene())

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
