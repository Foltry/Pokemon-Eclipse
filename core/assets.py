import gif_pygame
import pygame
import os

ASSETS_DIR = "assets"

def load_gif(path, scale=None):
    full_path = os.path.join(ASSETS_DIR, get_sprite_path(path))
    gif = gif_pygame.GIF(full_path)
    if scale:
        gif.scale(scale)
    return gif

def get_sprite_path(sprite_name: str) -> str:
    base_name = sprite_name.replace(".gif", "")
    id_part, variant = base_name.split("_", 1)

    folder = "front" if "front" in variant else "back"
    if "shiny" in variant:
        folder = f"shiny_{folder}"
    if "female" in variant:
        folder = f"female_{folder}" if "shiny" not in variant else f"shiny_female_{folder.split('_')[-1]}"

    return os.path.join("pokemon", folder, f"{id_part}.gif")
