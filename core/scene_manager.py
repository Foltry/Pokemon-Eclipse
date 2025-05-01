# core/scene_manager.py

class Scene:
    def __init__(self):
        self.manager = None

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass


class SceneManager:
    def __init__(self):
        self.scene_stack = []

    def change_scene(self, new_scene):
        """Empile une nouvelle scène (comme ouvrir un menu)."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
        self.scene_stack.append(new_scene)
        new_scene.manager = self
        new_scene.on_enter()

    def go_back(self):
        """Revient à la scène précédente sans en créer une nouvelle."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
            self.scene_stack.pop()

        if self.scene_stack:
            self.scene_stack[-1].on_enter()
            self.scene_stack[-1].manager = self

    @property
    def scene(self):
        """Retourne la scène active actuelle."""
        return self.scene_stack[-1] if self.scene_stack else None

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self, surface):
        if self.scene:
            self.scene.draw(surface)

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)
