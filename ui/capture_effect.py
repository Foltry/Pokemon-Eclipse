import pygame
import math

class CaptureEffect:
    def __init__(self, sprite, pos):
        self.sprite = sprite  # Peut être une Surface ou un GIFPygame
        self.pos = pos
        self.offset = (0, 0)

        self.scale = 1.0
        self.opacity = 255

        self.duration = 500  # durée d’une animation (in ou out) en ms
        self.elapsed = 0
        self.phase = None  # "in", "out", None
        self.active = False

        self.current_frame_index = 0  # nécessaire pour draw()

    def trigger_in(self):
        print("[ACTION] trigger_in()")
        self.phase = "in"
        self.elapsed = 0
        self.active = True
        self.scale = 1.0
        self.opacity = 255

    def trigger_out(self):
        if self.phase == "out" and self.active:
            print("[WARNING] trigger_out() ignoré (déjà lancé)")
            return
        print("[ACTION] trigger_out()")
        self.phase = "out"
        self.elapsed = 0
        self.active = True
        self.scale = 0.5
        self.opacity = 0


    def is_active(self):
        return self.active

    def current_phase(self):
        return self.phase

    def update(self, dt):
        if not self.active:
            return

        self.elapsed += dt
        t = min(self.elapsed / self.duration, 1)

        if self.phase == "in":
            self.scale = 1.0 - t
            self.opacity = int(255 * (1 - t))
        elif self.phase == "out":
            self.scale = t
            self.opacity = int(255 * t)

        if self.elapsed >= self.duration:
            self.active = False
            self.phase = None

    def draw(self, surface):
        if not self.is_active():
            return

        # Récupérer la frame (Surface)
        if isinstance(self.sprite, pygame.Surface):
            frame = self.sprite
        else:
            frame = self.sprite.blit_ready()

        # Adapter taille
        w, h = frame.get_width(), frame.get_height()
        new_size = (int(w * self.scale), int(h * self.scale))

        if frame.get_bitsize() in (24, 32):
            scaled = pygame.transform.smoothscale(frame, new_size)
        else:
            scaled = pygame.transform.scale(frame, new_size)

        # Appliquer l’opacité
        if scaled.get_alpha() is None:
            scaled = scaled.convert_alpha()
        scaled.set_alpha(self.opacity)

        # Position centrée
        pos_x = int(self.pos[0] + self.offset[0] - new_size[0] / 2)
        pos_y = int(self.pos[1] + self.offset[1] - new_size[1] / 2)

        surface.blit(scaled, (pos_x, pos_y))
