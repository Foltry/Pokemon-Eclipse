# battle/ai.py

import random
from battle.engine import calculate_damage

class BattleAI:
    def __init__(self, skill_level=0):
        self.skill_level = skill_level

    def choose_move(self, attacker, defender, moves):
        best_score = -float('inf')
        best_move = None

        for move in moves:
            # Ignorer les attaques sans puissance (par exemple, les attaques de statut)
            if move["power"] is None or move["power"] == 0:
                continue

            # Calcul des dégâts potentiels
            damage, is_crit, type_multiplier = calculate_damage(attacker, defender, move)

            # Calcul du score en fonction des dégâts et de la précision
            score = damage * (move.get("accuracy", 100) / 100)

            # Bonus pour les attaques super efficaces
            if type_multiplier > 1:
                score *= 1.5
            elif type_multiplier < 1:
                score *= 0.5

            # Bonus pour les effets secondaires
            if move.get("status") and self.skill_level >= 32:
                score += 10  # Arbitrary bonus for status effects

            # Mise à jour du meilleur score et de la meilleure attaque
            if score > best_score:
                best_score = score
                best_move = move

        # Si aucune attaque n'a été sélectionnée, choisir une attaque au hasard
        if best_move is None:
            best_move = random.choice(moves)

        return best_move
