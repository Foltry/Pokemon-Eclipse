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
            if move["power"] is None or move["power"] == 0:
                continue

            damage, is_crit, type_multiplier = calculate_damage(attacker, defender, move)

            score = damage * (move.get("accuracy", 100) / 100)

            # Bonus pour attaques super efficaces
            if type_multiplier > 1:
                score *= 1.5
            elif type_multiplier < 1:
                score *= 0.5

            # Bonus pour infliger un statut
            if move.get("effects", {}).get("status") and self.skill_level >= 32:
                score += 10

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            best_move = random.choice(moves)

        return best_move
