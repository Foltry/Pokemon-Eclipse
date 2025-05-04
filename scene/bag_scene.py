# scene/bag_scene.py

from core.scene_manager import Scene
from core.run_manager import run_manager
from ui.bag_menu import BagMenu

class BagScene(Scene):
    """
    Scène représentant l'ouverture du sac (inventaire du joueur).
    Permet la navigation et l'utilisation des objets.
    """
    
    def __init__(self):
        super().__init__()
        self.bag_menu = None

    def handle_event(self, event):
        """
        Gère les événements utilisateur (clavier/souris).
        """
        if self.bag_menu:
            self.bag_menu.handle_event(event, self.manager)

    def update(self, dt):
        """
        Met à jour les éléments de l'interface du sac.
        """
        if self.bag_menu:
            self.bag_menu.update(dt)

    def draw(self, screen):
        """
        Dessine le menu du sac à l'écran.
        """
        if self.bag_menu:
            self.bag_menu.draw(screen)

    def on_enter(self):
        """
        Initialise le menu du sac à l'entrée dans la scène.
        """
        inventory = run_manager.get_items_as_inventory()
        print(f"[DEBUG] Inventaire à l'entrée dans le sac : {inventory}")
        self.bag_menu = BagMenu(inventory)

    def on_exit(self):
        """
        Nettoie les références en quittant la scène.
        """
        self.bag_menu = None
