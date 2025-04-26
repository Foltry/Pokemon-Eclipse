# scene/starter_scene.py

import pygame
import random
import os
import json
import math
from core.scene_manager import Scene
from core.run_manager import run_manager
from scene.battle_scene import BattleScene

# Assets
BG_IMG = pygame.image.load(os.path.join("assets", "ui", "starter", "starter_bg.png"))
POKEBALL_IMG = pygame.image.load(os.path.join("assets", "ui", "starter", "pokeball.png"))

# Police
pygame.font.init()
FONT = pygame.font.Font(os.path.join("assets", "fonts", "power clear.ttf"), 16)

# Positionnement
CENTER_X = 240
Y_POS = 160
OFFSET = 100

class StarterScene(Scene):
    def __init__(self):
        self.selected_index = 1
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.starters = self.pick_starters()
        self.animation_phase = [0, 0, 0]

    def pick_starters(self):
        with open("data/starters.json", encoding="utf-8") as f:
            starter_list = json.load(f)

        types = {"grass": [], "fire": [], "water": []}
        for starter in starter_list:
            for t in starter["types"]:
                t_lower = t.lower()
                if t_lower in types:
                    types[t_lower].append(starter)
                    break

        if not all(types.values()):
            raise ValueError("❌ Impossible de générer les starters : un type est vide.")

        selected = [
            random.choice(types["grass"]),
            random.choice(types["fire"]),
            random.choice(types["water"]),
        ]
        random.shuffle(selected)
        return selected

    def on_enter(self):
        self.selected_index = 1
        self.timer = 0

    def update(self, dt):
        self.timer += self.clock.tick(60) / 1000

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(2, self.selected_index + 1)
            elif event.key == pygame.K_RETURN:
                chosen = self.starters[self.selected_index]
                run_manager.set_starters(self.starters)
                run_manager.add_pokemon_to_team(chosen)
                self.manager.change_scene(BattleScene())

    def draw(self, screen):
        screen.blit(BG_IMG, (0, 0))
        for i, poke in enumerate(self.starters):
            x = CENTER_X + (i - 1) * OFFSET
            y = Y_POS
            surf = POKEBALL_IMG.copy()

            if i == self.selected_index:
                wiggle_offset = int(5 * math.sin(self.timer * 12))
                rotation = 5 * math.sin(self.timer * 8)
                surf = pygame.transform.rotate(surf, rotation)
                y += wiggle_offset
                rect = surf.get_rect(center=(x, y))
            else:
                rect = surf.get_rect(center=(x, y))

            screen.blit(surf, rect.topleft)

            name_text = FONT.render(poke.get("name", "???"), True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(x, rect.top - 16))
            screen.blit(name_text, name_rect)
