class Item:
    def __init__(self, name, data):
        self.name = name
        self.effect = data["effect"]
        self.value = data["value"]

    def __repr__(self):
        return f"<Item {self.name} ({self.effect}: {self.value})>"
