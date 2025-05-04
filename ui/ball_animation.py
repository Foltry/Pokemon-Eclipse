# ui/ball_animation.py

import pygame
import os
import unicodedata


class BallAnimation:
    """
    Gère l'animation d'une Poké Ball lors d'une tentative de capture.

    Attributs :
        ball_type (str) : Type de Poké Ball (pokeball, superball, etc.)
        pos (tuple) : Position d'affichage (x, y)
        frame_duration (int) : Durée entre chaque frame en ms
    """

    def __init__(self, ball_type="pokeball", pos=(200, 150), frame_duration=80):
        self.ball_type = self._normalize_ball_type(ball_type)
        self.pos = pos
        self.frame_duration = frame_duration  # Durée entre chaque frame en ms

        # Chargement des frames
        base_path = os.path.join("assets", "ui", "balls")
        self.closed_path = os.path.join(base_path, f"{self.ball_type.upper()}.png")
        self.open_path = os.path.join(base_path, f"{self.ball_type.upper()}_OPEN.png")

        self.frames = []
        self.open_image = None
        self.load_images()

        self.current_frame = 0
        self.time_since_last_frame = 0
        self.animation_done = False
        self.playing = True
        self.show_open = False

    def _normalize_ball_type(self, ball_type):
        """Nettoie et normalise le nom de la Ball (ex : accents, majuscules)."""
        clean = ball_type.lower().replace(" ", "")
        return ''.join(c for c in unicodedata.normalize('NFD', clean) if unicodedata.category(c) != 'Mn')

    def load_images(self):
        """Charge les frames de l’animation fermée et l’image ouverte."""
        sheet = pygame.image.load(self.closed_path).convert_alpha()
        width = sheet.get_width() // 8
        height = sheet.get_height()

        self.frames = [
            sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            for i in range(8)
        ]

        self.open_image = pygame.image.load(self.open_path).convert_alpha()

    def update(self, dt):
        """Met à jour l’animation selon le temps écoulé (dt en ms)."""
        if not self.playing:
            return

        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.frame_duration:
            self.time_since_last_frame = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.playing = False
                self.show_open = True

    def draw(self, screen):
        """Affiche la Poké Ball selon son état actuel (animée, ouverte ou fixe)."""
        if self.playing:
            screen.blit(self.frames[self.current_frame], self.pos)
        elif self.show_open:
            screen.blit(self.open_image, self.pos)
        else:
            # En phase "tremblement" → première frame fixe
            screen.blit(self.frames[0], self.pos)

    def is_finished(self):
        """Renvoie True si l’animation complète est terminée et la Ball est ouverte."""
        return self.show_open
