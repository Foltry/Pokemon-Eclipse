# core/run_manager.py

"""
Gère l'état de la run actuelle du joueur, incluant son équipe et son inventaire.
"""

from data.pokemon_loader import get_all_pokemon
from data.items_loader import get_all_items

class RunManager:
    def __init__(self):
        # === Données principales ===
        self.team = []         # Équipe actuelle du joueur
        self.items = {}        # Inventaire du joueur
        self.starters = []     # Liste des starters possibles
        self.active = False    # Indique si une run est en cours

        # === Données de référence ===
        self.pokemon_data = get_all_pokemon()
        self.item_data = get_all_items()

    # ======================================================
    # === Pokémon Management ===
    # ======================================================

    def start_new_run(self):
        """
        Démarre une nouvelle run en réinitialisant l'équipe,
        l'inventaire, les starters et l'état actif.
        """
        self.team.clear()
        self.items.clear()
        self.starters.clear()
        self.active = True
        self.add_item("Potion", 1)

    def add_pokemon_to_team(self, pokemon):
        """
        Ajoute un Pokémon à l'équipe actuelle.

        Args:
            pokemon (dict): Données du Pokémon à ajouter.
        """
        self.team.append(pokemon)

    def has_team_space(self):
        """
        Vérifie s'il reste de la place dans l'équipe.

        Returns:
            bool: True si l'équipe a moins de 6 Pokémon.
        """
        return len(self.team) < 6

    def is_team_alive(self):
        """
        Vérifie si au moins un Pokémon de l'équipe a des PV.

        Returns:
            bool: True si l'équipe n'est pas totalement KO.
        """
        return any(p.get("stats", {}).get("hp", 0) > 0 for p in self.team)

    def get_team(self):
        """
        Retourne l'équipe actuelle.

        Returns:
            list: Liste des Pokémon dans l'équipe.
        """
        return self.team

    def set_starters(self, starter_list):
        """
        Définit les Pokémon starters proposés au joueur.

        Args:
            starter_list (list): Liste de Pokémon starters.
        """
        self.starters = starter_list

    def reset(self):
        """
        Réinitialise complètement la run en cours.
        """
        self.team.clear()
        self.items.clear()
        self.starters.clear()
        self.active = False

    # ======================================================
    # === Items Management ===
    # ======================================================

    def add_item(self, item_name: str, quantity: int = 1):
        """
        Ajoute un objet à l'inventaire.

        Args:
            item_name (str): Nom de l'objet.
            quantity (int): Quantité à ajouter.
        """
        if item_name in self.item_data:
            self.items[item_name] = self.items.get(item_name, 0) + quantity

    def get_items_as_inventory(self):
        """
        Retourne l'inventaire sous forme de liste exploitable par l'UI.

        Returns:
            list: Liste de dictionnaires {name, quantity}.
        """
        return [{"name": name, "quantity": qty} for name, qty in self.items.items()]

# Singleton de la run
run_manager = RunManager()
