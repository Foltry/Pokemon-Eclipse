import os, json

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

def generate_starters_data():
    starters = [
        "001", "004", "007",
        "152", "155", "158",
        "252", "255", "258",
        "387", "390", "393",
        "495", "498", "501"
    ]
    with open(os.path.join(DATA, "starters.json"), "w", encoding="utf-8") as f:
        json.dump(starters, f, indent=2)
