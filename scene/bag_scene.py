from core.scene_manager import Scene
from core.run_manager import run_manager
from ui.bag_menu import BagMenu

class BagScene(Scene):
    def __init__(self):
        self.bag_menu = None

    def handle_event(self, event):
        if self.bag_menu:
            self.bag_menu.handle_event(event, self.manager)

    def update(self, dt):
        if self.bag_menu:
            self.bag_menu.update(dt)

    def draw(self, screen):
        if self.bag_menu:
            self.bag_menu.draw(screen)

    def on_enter(self):
        inventory = run_manager.get_items_as_inventory()
        print(f"[DEBUG] Inventaire à l'entrée dans le sac : {inventory}")
        self.bag_menu = BagMenu(inventory)

    def on_exit(self):
        self.bag_menu = None
