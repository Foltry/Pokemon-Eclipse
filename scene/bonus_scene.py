import pygame
import random
from core.scene_manager import Scene
from core.run_manager import run_manager

FONT_PATH = "assets/fonts/power clear.ttf"
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

class BonusScene(Scene):
    def __init__(self):
        self.font_title = pygame.font.Font(FONT_PATH, 32)
        self.font_option = pygame.font.Font(FONT_PATH, 24)
        self.options = ["Soigner votre Pokémon", "Recevoir une Potion"]
        self.selected = 0
        self.cooldown = 0

    def on_enter(self):
        self.cooldown = 0

    def update(self, dt):
        self.cooldown = max(0, self.cooldown - dt)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.cooldown <= 0:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self.cooldown = 150
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self.cooldown = 150
            elif event.key == pygame.K_RETURN:
                self.apply_bonus(self.selected)

                # Import déplacé ici pour éviter l'import circulaire
                from scene.battle_scene import BattleScene
                self.manager.change_scene(BattleScene())

    def apply_bonus(self, index):
        if index == 0:
            for p in run_manager.team:
                p["current_hp"] = p.get("base_stats", {}).get("hp", 100)
        elif index == 1:
            run_manager.add_item("Potion", 1)

    def draw(self, screen):
        screen.fill((0, 0, 0))

        title = self.font_title.render("Choisissez un bonus :", True, YELLOW)
        screen.blit(title, (60, 80))

        for i, option in enumerate(self.options):
            color = RED if i == self.selected else WHITE
            text = self.font_option.render(option, True, color)
            screen.blit(text, (80, 150 + i * 50))
