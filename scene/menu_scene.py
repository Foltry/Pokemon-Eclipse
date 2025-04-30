import pygame
from core.scene_manager import Scene
from scene.starter_scene import StarterScene

FONT_PATH = "assets/fonts/power clear.ttf"
TITLE_COLOR = (255, 255, 0)
OPTION_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 0, 0)

class MenuScene(Scene):
    def __init__(self):
        self.options = ["Nouvelle aventure", "Quitter"]
        self.selected = 0
        self.font_title = pygame.font.Font(FONT_PATH, 48)
        self.font_option = pygame.font.Font(FONT_PATH, 28)
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
                if self.selected == 0:
                    self.manager.change_scene(StarterScene())
                elif self.selected == 1:
                    pygame.quit()
                    exit()

    def draw(self, screen):
        screen.fill((0, 0, 0))

        title_surf = self.font_title.render("Pokémon Eclipse", True, TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(240, 80))
        screen.blit(title_surf, title_rect)

        for i, option in enumerate(self.options):
            color = SELECTED_COLOR if i == self.selected else OPTION_COLOR
            option_surf = self.font_option.render(option, True, color)
            option_rect = option_surf.get_rect(center=(240, 200 + i * 50))
            screen.blit(option_surf, option_rect)
