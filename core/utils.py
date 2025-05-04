# core/utils.py

"""
Fonctions utilitaires globales pour le jeu.
"""

import pygame
import sys

def quit_game():
    """
    Ferme proprement le jeu en quittant Pygame et le programme.
    """
    pygame.quit()
    sys.exit()
