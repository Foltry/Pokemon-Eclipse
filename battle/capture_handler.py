import random
import math

# Modificateurs de statut
STATUS_MODIFIERS = {
    "sleep": 2.0,
    "freeze": 2.0,
    "paralysis": 1.5,
    "poison": 1.5,
    "burn": 1.5
}

# Modificateurs de Poké Balls (exemples de base)
BALL_MODIFIERS = {
    "poké ball": 1.0,
    "super ball": 1.5,
    "hyper ball": 2.0,
    "master ball": 255.0  # capture garantie
}

def get_ball_modifier(ball_name):
    return BALL_MODIFIERS.get(ball_name.lower(), 1.0)

def get_status_modifier(status):
    if not status:
        return 1.0
    return STATUS_MODIFIERS.get(status.lower(), 1.0)

def attempt_capture(pokemon, ball_name, status=None):
    """
    Tente de capturer un Pokémon avec la formule officielle.
    Renvoie un dict : {"success": bool, "shakes": int, "messages": list[str]}
    """
    max_hp = pokemon["stats"]["hp"]
    current_hp = pokemon["hp"]
    catch_rate = pokemon.get("base_capture_rate", 150)

    ball_mod = get_ball_modifier(ball_name)
    status_mod = get_status_modifier(status)

    # Master Ball = capture garantie
    if ball_mod >= 255:
        return {
            "success": True,
            "shakes": 3,
            "messages": [f"{pokemon['name']} est capturé avec une {ball_name} ! (master ball)"]
        }

    # Formule de base
    a = ((3 * max_hp - 2 * current_hp) * catch_rate * ball_mod * status_mod) / (3 * max_hp)

    if a >= 255:
        return {
            "success": True,
            "shakes": 3,
            "messages": [f"{pokemon['name']} est capturé avec une {ball_name} !"]
        }

    # Calcul du seuil b
    try:
        b = int(1048560 / math.sqrt(math.sqrt(16711680 / a)))
    except ZeroDivisionError:
        b = 0

    shakes = 0
    for _ in range(4):
        if random.randint(0, 65535) < b:
            shakes += 1
        else:
            break

    if shakes == 4:
        return {
            "success": True,
            "shakes": 3,
            "messages": [f"{pokemon['name']} est capturé !"]
        }
    else:
        return {
            "success": False,
            "shakes": shakes,
            "messages": [f"{pokemon['name']} s'est échappé !"]
        }

 