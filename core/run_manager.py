from core.models.pokemon import Pokemon
from core.models.item import Item
from core.data_loader import load_json

class RunManager:
    def __init__(self):
        self.team = []
        self.items = {}
        self.active = False

        self.pokemon_data = load_json("data/pokemon.json")
        self.item_data = load_json("data/items.json")

    def start_new_run(self):
        self.team.clear()
        self.items.clear()
        self.active = True

    def add_pokemon(self, pokemon_id: str):
        if pokemon_id in self.pokemon_data:
            pokemon = Pokemon(pokemon_id, self.pokemon_data[pokemon_id])
            self.team.append(pokemon)

    def add_item(self, item_name: str, quantity: int = 1):
        if item_name in self.item_data:
            if item_name not in self.items:
                self.items[item_name] = 0
            self.items[item_name] += quantity

    def is_team_alive(self):
        return any(p.hp > 0 for p in self.team)

    def reset(self):
        self.active = False
        self.team.clear()
        self.items.clear()
