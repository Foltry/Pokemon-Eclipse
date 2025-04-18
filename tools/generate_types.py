import os, json, requests

URL = "https://pokeapi.co/api/v2/type/"
PATH = "data/types.json"

types = {}
r = requests.get(URL)
if r.status_code == 200:
    for entry in r.json()["results"]:
        tid = entry["url"].split("/")[-2]
        t = requests.get(entry["url"])
        if t.status_code != 200: continue
        d = t.json()
        name = next((n["name"] for n in d["names"] if n["language"]["name"] == "fr"), d["name"])
        types[d["name"]] = {"id": tid, "name": name}

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(types, f, ensure_ascii=False, indent=2)