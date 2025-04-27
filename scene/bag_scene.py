# scene/bag_scene.py

import pygame
from core.scene_manager import Scene
from core.run_manager import run_manager
from ui.bag_menu import BagMenu

class BagScene(Scene):
    def __init__(self):
        # Récupération de l'inventaire depuis run_manager
        inventory = run_manager.get_items_as_inventory()
        self.bag_menu = BagMenu(inventory)

    def handle_event(self, event):
        self.bag_menu.handle_event(event, self.manager)

    def update(self, dt):
        self.bag_menu.update(dt)

    def draw(self, screen):
        self.bag_menu.draw(screen)

    def on_enter(self):
        pass

    def on_exit(self):
        pass
