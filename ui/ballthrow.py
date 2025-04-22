import pygame
import math
from ui.ball_animation import BallAnimation

class BallThrow:
    def __init__(self, ball_type, start_pos, target_pos, result, duration=500):
        self.ball_anim = BallAnimation(ball_type=ball_type, pos=start_pos)
        self.start_pos = pygame.Vector2(start_pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.duration = duration
        self.elapsed = 0
        self.peak_height = -80

        self.phase = "throw"
        self.result = result
        self.captured = result.get("success", False)
        self.shakes = result.get("shakes", 0)

        self.shake_index = 0
        self.shake_timer = 0
        self.shake_interval = 600  # Durée d’une secousse complète (ms)

        self.wait_timer = 0
        self.wait_after = 500

        self.original_pos = self.target_pos.xy
        self.ball_anim.playing = True
        self.ball_anim.show_open = False


    def update(self, dt):
        if self.phase == "throw":
            self.elapsed += dt
            t = min(self.elapsed / self.duration, 1)
            x = self.start_pos.x + (self.target_pos.x - self.start_pos.x) * t
            y = self.start_pos.y + (self.target_pos.y - self.start_pos.y) * t + self.peak_height * math.sin(math.pi * t)
            self.ball_anim.pos = (x, y)
            self.ball_anim.update(dt)

            if t >= 1:
                self.phase = "shake"
                self.shake_timer = 0
                self.shake_index = 0
                self.ball_anim.playing = False
                self.ball_anim.current_frame = 0
                self.ball_anim.show_open = False
                self.ball_anim.pos = self.original_pos

        elif self.phase == "shake":
            self.shake_timer += dt

            # Oscillation gauche-droite
            offset = 0
            if self.shake_index < self.shakes:
                phase = (self.shake_timer % self.shake_interval) / self.shake_interval
                offset = 8 * math.sin(2 * math.pi * phase)
                self.ball_anim.pos = (self.original_pos[0] + offset, self.original_pos[1])

                if self.shake_timer >= self.shake_interval:
                    self.shake_index += 1
                    self.shake_timer = 0
                    self.ball_anim.pos = self.original_pos
            else:
                self.phase = "wait"
                self.wait_timer = 0
                self.ball_anim.pos = self.original_pos

        elif self.phase == "wait":
            self.wait_timer += dt
            if self.wait_timer >= self.wait_after:
                self.phase = "done"
                if not self.captured:
                    self.ball_anim.show_open = True

        elif self.phase == "done":
            self.ball_anim.update(dt)

    def draw(self, screen):
        self.ball_anim.draw(screen)

    def is_done(self):
        return self.phase == "done"

    def has_landed(self):
        return self.phase != "throw"
