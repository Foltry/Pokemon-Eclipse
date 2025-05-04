# tools/assets.py

import os
import pygame
import gif_pygame

ASSETS_DIR = "assets"

def load_gif(path, scale=None):
    """
    Charge un fichier GIF animé à partir du répertoire des assets.

    Args:
        path (str): Chemin relatif au GIF depuis le dossier assets.
        scale (tuple[int, int], optional): Taille à appliquer au GIF (largeur, hauteur).

    Returns:
        gif_pygame.GIF: Objet GIF prêt à être utilisé.
    """
    full_path = os.path.join(ASSETS_DIR, get_sprite_path(path))
    gif = gif_pygame.GIF(full_path)
    if scale:
        gif.scale(scale)
    return gif

def get_sprite_path(sprite_name: str) -> str:
    """
    Déduit le chemin complet d’un sprite Pokémon à partir de son nom formaté.

    Le nom doit suivre le format : "<id>_<variant>", ex : "001_front", "025_shiny_back".

    Args:
        sprite_name (str): Nom du sprite avec suffixe (front, back, shiny, female...).

    Returns:
        str: Chemin relatif vers le fichier .gif dans le dossier assets/pokemon/
    """
    base_name = sprite_name.replace(".gif", "")
    id_part, variant = base_name.split("_", 1)

    folder = "front" if "front" in variant else "back"
    if "shiny" in variant:
        folder = f"shiny_{folder}"
    if "female" in variant:
        if "shiny" in variant:
            folder = f"shiny_female_{folder.split('_')[-1]}"
        else:
            folder = f"female_{folder}"

    return os.path.join("pokemon", folder, f"{id_part}.gif")

def load_image(path: str) -> pygame.Surface:
    """
    Charge une image depuis le dossier `assets/`.

    Args:
        path (str): Chemin relatif à l’image dans le dossier assets.

    Returns:
        pygame.Surface: Surface de l’image avec transparence activée.

    Raises:
        FileNotFoundError: Si le fichier est introuvable.
    """
    full_path = os.path.join(ASSETS_DIR, path)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Image not found: {full_path}")
    return pygame.image.load(full_path).convert_alpha()
