import pygame
import os

class BallAnimation:
    def __init__(self, ball_type="pokeball", pos=(200, 150), frame_duration=80):
        self.ball_type = ball_type.lower().replace(" ", "")
        import unicodedata
        # Supprimer les accents
        self.ball_type = ''.join(
            c for c in unicodedata.normalize('NFD', self.ball_type)
            if unicodedata.category(c) != 'Mn'
        )

        self.pos = pos
        self.frame_duration = frame_duration  # ms entre frames

        # Chemins d’accès
        base_path = os.path.join("assets", "ui", "balls")
        self.closed_path = os.path.join(base_path, f"{self.ball_type.upper()}.png")
        self.open_path = os.path.join(base_path, f"{self.ball_type.upper()}_OPEN.png")

        # Sprites
        self.frames = []
        self.open_image = None
        self.load_images()

        self.current_frame = 0
        self.time_since_last_frame = 0
        self.animation_done = False
        self.playing = True
        self.show_open = False

    def load_images(self):
        sheet = pygame.image.load(self.closed_path).convert_alpha()
        width = sheet.get_width() // 8
        height = sheet.get_height()

        self.frames = [
            sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            for i in range(8)
        ]

        self.open_image = pygame.image.load(self.open_path).convert_alpha()

    def update(self, dt):
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
        if self.playing:
            screen.blit(self.frames[self.current_frame], self.pos)
        elif self.show_open:
            screen.blit(self.open_image, self.pos)
        else:
            # En phase de shake : toujours première frame
            screen.blit(self.frames[0], self.pos)


    def is_finished(self):
        return self.show_open
