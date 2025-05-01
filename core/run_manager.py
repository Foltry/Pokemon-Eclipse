# core/run_manager.py

from data.pokemon_loader import get_all_pokemon
from data.items_loader import get_all_items

class RunManager:
    def __init__(self):
        # --- Données principales ---
        self.team = []         # Équipe actuelle du joueur
        self.items = {}        # Inventaire du joueur
        self.starters = []     # Liste des starters possibles
        self.active = False    # Indique si une run est en cours

        # --- Chargement données de base ---
        self.pokemon_data = get_all_pokemon()
        self.item_data = get_all_items()

    # ======================================================
    # Pokémon Management
    # ======================================================

    def start_new_run(self):
        """Démarre une nouvelle run."""
        self.team.clear()
        self.items.clear()
        self.starters.clear()
        self.active = True

        self.add_item("Potion", 1)

    def add_pokemon_to_team(self, pokemon):
        """Ajoute un Pokémon à l'équipe."""
        self.team.append(pokemon)

    def has_team_space(self):
        """Retourne True si l'équipe a moins de 6 Pokémon."""
        return len(self.team) < 6

    def is_team_alive(self):
        """Retourne True si au moins un Pokémon a des PV."""
        return any(p.get("stats", {}).get("hp", 0) > 0 for p in self.team)

    def get_team(self):
        """Retourne l'équipe actuelle."""
        return self.team

    def set_starters(self, starter_list):
        """Définit les starters pour le début de la run."""
        self.starters = starter_list

    def reset(self):
        """Réinitialise complètement la run."""
        self.team.clear()
        self.items.clear()
        self.starters.clear()
        self.active = False

    # ======================================================
    # Items Management
    # ======================================================

    def add_item(self, item_name: str, quantity: int = 1):
        """Ajoute un objet à l'inventaire."""
        if item_name in self.item_data:
            self.items[item_name] = self.items.get(item_name, 0) + quantity

    def get_items_as_inventory(self):
        """
        Retourne les objets possédés sous forme de liste :
        [{"name": nom, "quantity": quantité}, ...]
        """
        return [{"name": name, "quantity": qty} for name, qty in self.items.items()]

# Singleton de la run
run_manager = RunManager()
