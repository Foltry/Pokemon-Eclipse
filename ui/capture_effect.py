import pygame

class CaptureEffect:
    """
    Gère un effet visuel de capture avec transition (scale + opacity).
    Peut être utilisé avec un sprite statique ou animé (GIFPygame).
    """

    def __init__(self, sprite, pos):
        """
        Initialise l’effet de capture.

        Args:
            sprite (pygame.Surface | gif_pygame.GIFPygame): Sprite à afficher.
            pos (tuple): Position centrale (x, y) de l’effet.
        """
        self.sprite = sprite
        self.pos = pos
        self.offset = (0, 0)

        self.scale = 1.0
        self.opacity = 255

        self.duration = 500  # Durée de transition (in ou out) en ms
        self.elapsed = 0
        self.phase = None  # "in", "out", ou None
        self.active = False

    def trigger_in(self):
        """Déclenche l’animation de disparition (fade out + shrink)."""
        self.phase = "in"
        self.elapsed = 0
        self.active = True
        self.scale = 1.0
        self.opacity = 255

    def trigger_out(self):
        """Déclenche l’animation d’apparition (fade in + grow)."""
        if self.phase == "out" and self.active:
            return
        self.phase = "out"
        self.elapsed = 0
        self.active = True
        self.scale = 0.5
        self.opacity = 0

    def is_active(self):
        """Renvoie True si l’animation est en cours."""
        return self.active

    def current_phase(self):
        """Renvoie la phase actuelle : 'in', 'out' ou None."""
        return self.phase

    def update(self, dt):
        """
        Met à jour l’état de l’animation.

        Args:
            dt (int): Temps écoulé depuis la dernière frame (en ms).
        """
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
        """
        Dessine le sprite à l’écran avec échelle et opacité dynamiques.

        Args:
            surface (pygame.Surface): Surface cible.
        """
        if not self.is_active():
            return

        frame = self.sprite if isinstance(self.sprite, pygame.Surface) else self.sprite.blit_ready()
        w, h = frame.get_width(), frame.get_height()
        new_size = (int(w * self.scale), int(h * self.scale))

        # Redimensionnement adapté
        scaled = (
            pygame.transform.smoothscale(frame, new_size)
            if frame.get_bitsize() in (24, 32)
            else pygame.transform.scale(frame, new_size)
        )

        # Appliquer alpha
        if scaled.get_alpha() is None:
            scaled = scaled.convert_alpha()
        scaled.set_alpha(self.opacity)

        # Position centrée
        pos_x = int(self.pos[0] + self.offset[0] - new_size[0] / 2)
        pos_y = int(self.pos[1] + self.offset[1] - new_size[1] / 2)

        surface.blit(scaled, (pos_x, pos_y))
