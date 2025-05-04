# battle/capture_handler.py

import random
import math

# Modificateurs appliqués selon le statut du Pokémon
STATUS_MODIFIERS = {
    "sleep": 2.0,
    "freeze": 2.0,
    "paralysis": 1.5,
    "poison": 1.5,
    "burn": 1.5
}

# Modificateurs des types de Poké Balls
BALL_MODIFIERS = {
    "poké ball": 1.0,
    "super ball": 1.5,
    "hyper ball": 2.0,
    "master ball": 255.0  # capture garantie
}

def get_ball_modifier(ball_name):
    """
    Renvoie le multiplicateur associé à une Poké Ball.

    Args:
        ball_name (str): Le nom de la Poké Ball.

    Returns:
        float: Le multiplicateur de capture.
    """
    return BALL_MODIFIERS.get(ball_name.lower(), 1.0)

def get_status_modifier(status):
    """
    Renvoie le multiplicateur associé à un statut.

    Args:
        status (str): Le statut du Pokémon (ex: "sleep", "burn").

    Returns:
        float: Le multiplicateur de capture selon le statut.
    """
    if not status:
        return 1.0
    return STATUS_MODIFIERS.get(status.lower(), 1.0)

def attempt_capture(pokemon, ball_name, status=None):
    """
    Tente de capturer un Pokémon en utilisant la formule officielle.

    Args:
        pokemon (dict): Dictionnaire contenant les infos du Pokémon (hp, stats, capture rate...).
        ball_name (str): Type de Poké Ball utilisée.
        status (str, optional): Statut du Pokémon (par défaut: None).

    Returns:
        dict: {
            "success": bool,
            "shakes": int,
            "messages": list[str]
        }
    """
    max_hp = pokemon["stats"]["hp"]
    current_hp = pokemon["hp"]
    catch_rate = pokemon.get("base_capture_rate", 150)

    ball_mod = get_ball_modifier(ball_name)
    status_mod = get_status_modifier(status)

    # Master Ball = réussite automatique
    if ball_mod >= 255:
        return {
            "success": True,
            "shakes": 3,
            "messages": [f"{pokemon['name']} est capturé !"]
        }

    # Calcul du taux de capture
    a = ((3 * max_hp - 2 * current_hp) * catch_rate * ball_mod * status_mod) / (3 * max_hp)

    if a >= 255:
        return {
            "success": True,
            "shakes": 3,
            "messages": [f"{pokemon['name']} est capturé !"]
        }

    # Calcul du seuil b (probabilité de secousses)
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
    
    return {
        "success": False,
        "shakes": shakes,
        "messages": [f"{pokemon['name']} s'est échappé !"]
    }
