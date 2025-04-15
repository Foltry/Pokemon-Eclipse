class Pokemon:
    def __init__(self, id_, data):
        self.id = id_
        self.name = data["name"]
        self.types = data["types"]
        self.hp = data["base_hp"]
        self.attack = data["base_attack"]
        self.defense = data["base_defense"]
        self.moves = data["moves"]

    def __repr__(self):
        return f"<Pokemon {self.name} ({'/'.join(self.types)}) HP:{self.hp}>"
