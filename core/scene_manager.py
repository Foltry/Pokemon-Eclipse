# core/scene_manager.py

class SceneManager:
    def __init__(self):
        self.scene = None

    def change_scene(self, scene):
        if self.scene:
            self.scene.on_exit()
        self.scene = scene
        self.scene.on_enter()

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)

    def draw(self, surface):
        if self.scene:
            self.scene.draw(surface)
