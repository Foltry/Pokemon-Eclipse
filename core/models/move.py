class Move:
    def __init__(self, name, data):
        self.name = name
        self.power = data["power"]
        self.type = data["type"]

    def __repr__(self):
        return f"<Move {self.name} (Type: {self.type}, Power: {self.power})>"
