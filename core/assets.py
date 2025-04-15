import gif_pygame
import pygame
import os

ASSETS_DIR = "assets"

def load_gif(path, scale=None):
    full_path = os.path.join(ASSETS_DIR, path)
    gif = gif_pygame.GIF(full_path)
    if scale:
        gif.scale(scale)
    return gif
