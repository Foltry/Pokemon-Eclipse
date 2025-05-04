# battle/ai.py

import random
from battle.engine import calculate_damage

class BattleAI:
    """
    Intelligence artificielle de combat pour choisir les attaques selon un niveau de compétence.
    
    Attributes:
        skill_level (int): Niveau de compétence de l'IA, influence la prise en compte des effets de statut.
    """
    def __init__(self, skill_level=0):
        """
        Initialise une instance de l'IA avec un niveau de compétence donné.

        Args:
            skill_level (int): Niveau de compétence de l'IA (par défaut : 0).
        """
        self.skill_level = skill_level

    def choose_move(self, attacker, defender, moves):
        """
        Choisit la meilleure attaque à utiliser parmi celles disponibles.

        Args:
            attacker (dict): Dictionnaire représentant le Pokémon attaquant.
            defender (dict): Dictionnaire représentant le Pokémon défenseur.
            moves (list): Liste des attaques disponibles (chaque attaque est un dictionnaire).

        Returns:
            dict: L'attaque choisie.
        """
        best_score = float("-inf")
        best_move = None

        for move in moves:
            power = move.get("power")
            if not power:
                continue

            damage, _, type_multiplier = calculate_damage(attacker, defender, move)

            score = damage * (move.get("accuracy", 100) / 100)

            if type_multiplier > 1:
                score *= 1.5
            elif type_multiplier < 1:
                score *= 0.5

            if move.get("effects", {}).get("status") and self.skill_level >= 32:
                score += 10

            if score > best_score:
                best_score = score
                best_move = move

        return best_move if best_move else random.choice(moves)
