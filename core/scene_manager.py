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
        self.scene = None

    def change_scene(self, new_scene):
        if self.scene:
            self.scene.on_exit()  # ✅ Corrigé ici
        self.scene = new_scene
        self.scene.manager = self
        self.scene.on_enter()

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self, surface):
        if self.scene:
            self.scene.draw(surface)

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)
