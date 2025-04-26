# core/run_manager.py

from data.pokemon_loader import get_all_pokemon
from data.items_loader import get_all_items

class RunManager:
    def __init__(self):
        self.team = []
        self.items = {}
        self.active = False

        self.pokemon_data = get_all_pokemon()
        self.item_data = get_all_items()

        self.starters = []

    def start_new_run(self):
        self.team.clear()
        self.items.clear()
        self.active = True

    def add_pokemon_to_team(self, pokemon):
        self.team.append(pokemon)

    def add_item(self, item_name: str, quantity: int = 1):
        if item_name in self.item_data:
            if item_name not in self.items:
                self.items[item_name] = 0
            self.items[item_name] += quantity

    def is_team_alive(self):
        return any(p.get("stats", {}).get("hp", 0) > 0 for p in self.team)

    def set_starters(self, starter_list):
        self.starters = starter_list

    def get_team(self):
        return self.team

    def reset(self):
        self.team = []
        self.items = {}
        self.starters = []
        self.active = False

run_manager = RunManager()
