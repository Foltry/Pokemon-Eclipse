import pygame
import random
import os
import json
import math
from core.scene_manager import Scene
from core.run_manager import run_manager

POKEBALL_IMG = pygame.image.load(os.path.join("assets", "ui", "starter", "pokeball.png"))
BG_IMG = pygame.image.load(os.path.join("assets", "ui", "starter", "starter_bg.png"))

CENTER_X = 240
Y_POS = 160
OFFSET = 100

class StarterScene(Scene):
    def __init__(self):
        self.selected_index = 1  # Centre par défaut
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.pokeballs = self.load_starters()
        self.animation_phase = [0, 0, 0]  # Une phase d'animation pour chaque pokéball

    def load_starters(self):
        with open("data/starters.json", encoding="utf-8") as f:
            starters = json.load(f)
        return random.sample(starters, 3)

    def update(self,dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.selected_index = max(0, self.selected_index - 1)
            pygame.time.wait(150)
        elif keys[pygame.K_RIGHT]:
            self.selected_index = min(2, self.selected_index + 1)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            chosen = self.pokeballs[self.selected_index]
            run_manager.set_starters(self.pokeballs)
            run_manager.add_pokemon_to_team(chosen)
            from scene.battle_scene import BattleScene
            self.manager.change_scene(BattleScene())  # Test : enchaîner vers le combat

    def draw(self, screen):
        screen.blit(BG_IMG, (0, 0))
        self.timer += self.clock.tick(60) / 1000  # secondes

        for i, starter in enumerate(self.pokeballs):
            x = CENTER_X + (i - 1) * OFFSET
            y = Y_POS
            surf = POKEBALL_IMG.copy()

            if i == self.selected_index:
                wiggle_offset = int(5 * math.sin(self.timer * 10))
                rotation = 5 * math.sin(self.timer * 6)
                surf = pygame.transform.rotate(surf, rotation)
                y += wiggle_offset
                rect = surf.get_rect(center=(x, y))
            else:
                rect = surf.get_rect(center=(x, y))

            screen.blit(surf, rect.topleft)
