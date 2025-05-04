# core/scene_manager.py

"""
Gestionnaire de scènes pour le jeu (ex: menu, combat, carte).
Permet de gérer une pile de scènes actives (empilement/dépilement).
"""

class Scene:
    """
    Classe de base pour toutes les scènes du jeu.
    Les classes de scènes spécifiques doivent hériter de celle-ci.
    """
    def __init__(self):
        self.manager = None

    def on_enter(self):
        """Appelé lorsqu'on entre dans la scène."""
        pass

    def on_exit(self):
        """Appelé lorsqu'on quitte la scène."""
        pass

    def update(self, dt):
        """
        Met à jour la logique de la scène.

        Args:
            dt (float): Temps écoulé depuis la dernière frame.
        """
        pass

    def draw(self, surface):
        """
        Dessine la scène à l'écran.

        Args:
            surface (pygame.Surface): Surface cible pour l'affichage.
        """
        pass

    def handle_event(self, event):
        """
        Gère les événements utilisateur (clavier, souris...).

        Args:
            event (pygame.event.Event): Événement à traiter.
        """
        pass


class SceneManager:
    """
    Gère l'empilement des scènes et la transition entre elles.
    """

    def __init__(self):
        self.scene_stack = []

    def change_scene(self, new_scene):
        """
        Remplace la scène actuelle par une nouvelle.

        Args:
            new_scene (Scene): Nouvelle scène à activer.
        """
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
        self.scene_stack.append(new_scene)
        new_scene.manager = self
        new_scene.on_enter()

    def go_back(self):
        """
        Revient à la scène précédente dans la pile.
        """
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
            self.scene_stack.pop()

        if self.scene_stack:
            self.scene_stack[-1].on_enter()
            self.scene_stack[-1].manager = self

    @property
    def scene(self):
        """
        Retourne la scène actuellement active.

        Returns:
            Scene | None: Scène en haut de la pile ou None.
        """
        return self.scene_stack[-1] if self.scene_stack else None

    def update(self, dt):
        """
        Met à jour la scène active.

        Args:
            dt (float): Temps écoulé depuis la dernière frame.
        """
        if self.scene:
            self.scene.update(dt)

    def draw(self, surface):
        """
        Dessine la scène active.

        Args:
            surface (pygame.Surface): Surface d'affichage.
        """
        if self.scene:
            self.scene.draw(surface)

    def handle_event(self, event):
        """
        Transmet un événement à la scène active.

        Args:
            event (pygame.event.Event): Événement utilisateur.
        """
        if self.scene:
            self.scene.handle_event(event)
