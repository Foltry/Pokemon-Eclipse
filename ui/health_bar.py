# ui/health_bar.py

import pygame

class HealthBar:
    """
    Barre de points de vie avec animation fluide et code couleur.
    """

    def __init__(self, pos, size, max_hp, colors=None):
        """
        Initialise la barre de PV.

        Args:
            pos (tuple): Coordonnées (x, y) de la barre.
            size (tuple): Taille (largeur, hauteur) de la barre.
            max_hp (int): PV maximum.
            colors (dict, optional): Couleurs selon la proportion de PV restante.
        """
        self.x, self.y = pos
        self.width, self.height = size
        self.max_hp = max_hp

        self.current_hp = max_hp
        self.displayed_hp = max_hp

        self.start_hp = max_hp
        self.target_hp = max_hp
        self.animating = False
        self.animation_elapsed = 0
        self.animation_duration = 0.7  # en secondes

        self.colors = colors or {
            "high": (0, 192, 0),       # > 50%
            "medium": (232, 192, 0),   # entre 20% et 50%
            "low": (240, 64, 48)       # < 20%
        }

    def update(self, current_hp, dt):
        """
        Met à jour la barre en animant la transition de PV.

        Args:
            current_hp (int): Valeur actuelle réelle de PV.
            dt (float): Temps écoulé depuis la dernière frame (en secondes).
        """
        current_hp = max(0, min(current_hp, self.max_hp))
        self.current_hp = current_hp

        if current_hp != self.target_hp:
            self.start_hp = self.displayed_hp
            self.target_hp = current_hp
            self.animation_elapsed = 0
            self.animating = True

        if self.animating:
            self.animation_elapsed += dt
            t = min(self.animation_elapsed / self.animation_duration, 1.0)
            self.displayed_hp = self.start_hp + (self.target_hp - self.start_hp) * t
            if t >= 1.0:
                self.displayed_hp = self.target_hp
                self.animating = False

    def draw(self, surface):
        """
        Dessine la barre de PV sur la surface cible ainsi que le texte "PV actuels / max" (allié uniquement).
        """
        if self.max_hp <= 0:
            return

        # --- Couleur en fonction du ratio de PV ---
        ratio = self.displayed_hp / self.max_hp
        if ratio > 0.5:
            color = self.colors["high"]
        elif ratio > 0.2:
            color = self.colors["medium"]
        else:
            color = self.colors["low"]

        # --- Dessin de la barre de PV ---
        fill_width = int(self.width * ratio)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
        pygame.draw.rect(surface, color, fill_rect)

        # --- Affichage statique du texte pour le Pokémon allié uniquement ---
        if self.x == 402 and self.y == 232:  # ← coordonnées spécifiques à la barre du joueur
            font = pygame.font.Font("assets/fonts/power clear bold.ttf", 23)
            current = int(round(self.displayed_hp))
            hp_text = f"{current}/{self.max_hp}"
            text_surface = font.render(hp_text, True, (80, 80, 84))

            # Coordonnées fixes sous la barre alliée
            surface.blit(text_surface, (413, 242))
