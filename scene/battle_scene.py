# scene/battle_scene.py — Section 1 : Importations & Initialisation

import random
import time
import pygame

from core.scene_manager import Scene
from core.run_manager import run_manager

from battle.capture_handler import attempt_capture
from battle.enemy_selector import get_balanced_enemy

from data.pokemon_loader import get_learnable_moves

from ui.battle_ui import (
    load_battle_ui,
    load_combat_sprites,
    draw_combat_scene,
    XPBar,
    HealthBar
)
from ui.bonus_ui import BonusUI
from ui.animated_text import AnimatedText
from ui.fight_menu import FightMenu
from ui.capture_effect import CaptureEffect
from ui.ballthrow import BallThrow
from ui.pokemon_menu import PokemonMenu


class BattleScene(Scene):
    """
    Scène principale de combat.
    Gère l’affichage, les états, les menus, l’IA, les attaques et la capture.
    """

    def __init__(self):
        """Initialise tous les éléments nécessaires pour un combat."""

        # === UI Principale ===
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.font = pygame.font.Font("assets/fonts/power green.ttf", 18)
        self.bonus_ui = BonusUI(pos=(300, 300), spacing=34)
        self.button_grid = [[0, 1], [2, 3]]

        # === États de combat ===
        self.grid_pos = [0, 0]
        self.selected_index = 0
        self.state = "command"
        self.message_queue = []
        self.victory_handled = False
        self.show_bonus = False
        self.bonus_options = []
        self.bonus_message = None
        self.pokemon_menu = None

        # === Effets visuels & animations ===
        self.throw_animation = None
        self.capture_effect = None
        self.ball_throw = None
        self.capture_result = None
        self.hide_enemy_sprite = False
        self.ball_animation = None

        # === Préparation de l'équipe du joueur ===
        for pkm in run_manager.get_team():
            pkm.setdefault("level", 5)
            pkm.setdefault("stats", pkm.get("base_stats", {}))
            pkm.setdefault("hp", pkm["stats"].get("hp", 20))
            if "moves" not in pkm or not pkm["moves"]:
                pkm["moves"] = get_learnable_moves(pkm["id"], pkm["level"])

        starter = run_manager.get_team()[0]
        self.ally_id = starter["id"]
        self.ally_name = starter["name"]
        self.ally_level = starter["level"]
        self.ally_max_hp = starter["stats"]["hp"]
        self.ally_hp = min(starter["hp"], self.ally_max_hp)

        self.ally_hp_bar = HealthBar((402, 232), (98, 9), self.ally_max_hp)
        self.ally_hp_bar.current_hp = self.ally_hp
        self.ally_hp_bar.displayed_hp = self.ally_hp

        self.ally_xp = 0
        self.ally_max_xp = 1
        self.update_ally_xp()
        self.ally_xp_bar = XPBar((308, 267), self.ally_max_xp)
        self.ally_xp_bar.displayed_xp = self.ally_xp

        # === Génération de l’adversaire équilibré ===
        base_enemy = get_balanced_enemy(starter)
        self.enemy_id = base_enemy["id"]
        self.enemy_name = base_enemy["name"]
        self.enemy_level = base_enemy["level"]

        self.enemy_data = base_enemy.copy()
        self.enemy_data["stats"] = base_enemy["stats"]
        self.enemy_data["hp"] = base_enemy["stats"]["hp"]
        self.enemy_data["moves"] = get_learnable_moves(base_enemy["id"], base_enemy["level"])
        self.enemy_data["gender"] = self.enemy_gender = random.choice(["♂", "♀"])
        self.enemy_base_exp = base_enemy.get("base_experience", 50)
        self.enemy_hp = self.enemy_max_hp = self.enemy_data["hp"]

        self.enemy_hp_bar = HealthBar((116, 73), (98, 9), self.enemy_max_hp)
        self.enemy_hp_bar.current_hp = self.enemy_hp
        self.enemy_hp_bar.displayed_hp = self.enemy_hp

        # === Chargement des sprites ===
        self.bases, self.sprites, self.sprite_positions = load_combat_sprites(self.ally_id, self.enemy_id)
        self.capture_effect = CaptureEffect(sprite=self.sprites[1], pos=(360, 130))
        self.fight_menu = None

    def enemy_turn(self):
        """
        Le Pokémon ennemi choisit une attaque aléatoire et l'utilise sur l'allié.
        Applique les effets et met à jour les PV alliés.
        """
        if self.enemy_hp <= 0:
            return

        move = random.choice(self.enemy_data["moves"])
        attacker = {
            "name": self.enemy_name,
            "level": self.enemy_level,
            "types": self.enemy_data.get("types", []),
            "stats": self.enemy_data["stats"]
        }
        defender = run_manager.get_team()[0]
        defender.setdefault("stats", defender.get("base_stats", {}))
        defender.setdefault("hp", defender["stats"].get("hp", 1))

        self.queue_message(f"{self.enemy_name} utilise {move['name']} !")

        from battle.move_handler import use_move as core_use_move
        result = core_use_move(attacker, defender, move)
        for msg in result["messages"]:
            self.queue_message(msg)

        self.ally_hp = defender["hp"]

    def queue_message(self, text_or_callable):
        """
        Ajoute un message animé ou une fonction différée à la file des messages.
        """
        if isinstance(text_or_callable, str):
            y = 300 + (85 - self.font.get_height()) // 2
            animated = AnimatedText(text_or_callable, self.font, (40, y), speed=50)
            self.message_queue.append(animated)
        elif callable(text_or_callable):
            self.message_queue.append(text_or_callable)

    def use_move(self, move):
        """
        Applique une attaque lancée par le Pokémon allié contre l’ennemi.
        Affiche les messages associés et enchaîne le tour de l’ennemi si nécessaire.
        """
        from battle.move_handler import use_move as core_use_move
        starter = run_manager.get_team()[0]

        self.ally_hp = starter.get("hp", starter["stats"]["hp"])
        self.ally_max_hp = starter["stats"]["hp"]

        attacker = {
            "name": starter["name"],
            "level": starter.get("level", 5),
            "types": starter.get("types", []),
            "stats": starter.get("stats") or starter.get("base_stats")
        }
        defender = self.enemy_data

        if "hp" not in defender:
            defender["hp"] = defender["stats"]["hp"]

        self.queue_message(f"{self.ally_name} utilise {move['name']} !")
        result = core_use_move(attacker, defender, move)

        for msg in result["messages"]:
            self.queue_message(msg)

        def apply_player_damage():
            if result["deferred_damage"]:
                defender["hp"] = max(0, defender["hp"] - result["deferred_damage"])
            self.enemy_hp = defender["hp"]

        self.message_queue.append(apply_player_damage)

        if defender["hp"] <= 0:
            self.queue_message(f"{defender['name']} est K.O. !")
            self.hide_enemy_sprite = True
            self.message_queue.append(self.handle_victory)
        else:
            def delayed_enemy_turn():
                move = random.choice(self.enemy_data["moves"])
                self.queue_message(f"{self.enemy_name} utilise {move['name']} !")

                attacker = {
                    "name": self.enemy_name,
                    "level": self.enemy_level,
                    "types": self.enemy_data.get("types", []),
                    "stats": self.enemy_data["stats"]
                }
                defender = run_manager.get_team()[0]
                defender.setdefault("stats", defender.get("base_stats", {}))
                defender.setdefault("hp", defender["stats"].get("hp", 1))

                result = core_use_move(attacker, defender, move)

                for msg in result["messages"]:
                    self.queue_message(msg)

                def apply_enemy_damage():
                    if result["deferred_damage"]:
                        defender["hp"] = max(0, defender["hp"] - result["deferred_damage"])
                        self.ally_hp = defender["hp"]

                self.message_queue.append(apply_enemy_damage)

            self.message_queue.append(delayed_enemy_turn)

        self.state = "command"

    def xp_required(self, level):
        """
        Calcule l’expérience nécessaire pour atteindre un niveau donné.
        
        Args:
            level (int): Niveau cible.

        Returns:
            int: Expérience nécessaire.
        """
        return level ** 3

    def check_level_up(self, pokemon, queue_message):
        """
        Vérifie si un Pokémon monte de niveau, ajuste ses statistiques et déclenche une évolution si nécessaire.

        Args:
            pokemon (dict): Le Pokémon concerné.
            queue_message (callable): Fonction pour afficher les messages différés.
        """
        leveled_up = False

        while pokemon["xp"] >= self.xp_required(pokemon["level"] + 1):
            pokemon["level"] += 1
            leveled_up = True
            queue_message(f"{pokemon['name']} monte au niveau {pokemon['level']} !")

            for stat, base in pokemon.get("base_stats", {}).items():
                increase = base / 50
                pokemon["stats"][stat] = int(pokemon["stats"][stat] + increase)
                if stat == "hp":
                    pokemon["hp"] = pokemon["stats"]["hp"]

            from battle.evolution_handler import check_and_apply_evolution
            old_name = pokemon["name"]
            evolved = check_and_apply_evolution(pokemon)
            if evolved:
                queue_message(f"{old_name} évolue en {evolved['name']} !")

                def apply_evolution_update():
                    if run_manager.get_team()[0]["id"] == pokemon["id"]:
                        self.ally_id = pokemon["id"]
                        self.ally_name = pokemon["name"]
                        self.ally_max_hp = pokemon["stats"]["hp"]
                        self.ally_hp = pokemon["hp"]
                        self.bases, self.sprites, self.sprite_positions = load_combat_sprites(self.ally_id, self.enemy_id)

                self.message_queue.append(apply_evolution_update)

        if leveled_up and run_manager.get_team()[0]["id"] == pokemon["id"]:
            # On recalcule correctement l’XP affichée après level-up
            self.update_ally_xp()

    def show_end_bonus(self, items):
        """
        Affiche l’interface de sélection de bonus à la fin d’un combat.

        Args:
            items (list): Liste d’objets possibles à offrir.
        """
        self.bonus_options = random.sample(items, 2)
        self.bonus_ui.set_items(self.bonus_options)
        self.show_bonus = True

        y = 300 + (85 - self.font.get_height()) // 2
        self.bonus_message = AnimatedText("Choisissez un objet :", self.font, (40, y), speed=50)

    def handle_victory(self):
        """
        Gère la fin d’un combat gagné : XP, évolution, bonus, etc.
        """
        from battle.evolution_handler import check_evolution
        from data.items_loader import list_available_items

        self.victory_handled = True

        starter = run_manager.get_team()[0]
        self.ally_level = starter.get("level", 5)

        xp_gain = int((self.enemy_base_exp * self.enemy_level) / (5 + self.ally_level / 2))

        for i, poke in enumerate(run_manager.get_team()):
            old_level = poke["level"]
            poke["xp"] = poke.get("xp", 0) + xp_gain

            if i == 0:
                def xp_gain_sequence(p=poke, gain=xp_gain, old_lvl=old_level):
                    self.update_ally_xp()
                    self.queue_message(f"{p['name']} gagne {gain} XP !")

                    def after_xp():
                        if p["level"] > old_lvl:
                            self.queue_message(f"{p['name']} monte au niveau {p['level']} !")
                        self.check_level_up(p, self.queue_message)

                    self.message_queue.append(after_xp)

                self.message_queue.append(xp_gain_sequence)
            else:
                self.queue_message(f"{poke['name']} gagne {xp_gain} XP !")
                self.check_level_up(poke, self.queue_message)

            if poke["level"] > old_level:
                evolved_data = check_evolution(poke)
                if evolved_data:
                    old_name = poke["name"]
                    poke.update({
                        "id": evolved_data["id"],
                        "name": evolved_data["name"],
                        "stats": evolved_data["stats"],
                        "base_stats": evolved_data["stats"],
                        "types": evolved_data["types"],
                        "sprites": evolved_data["sprites"],
                        "moves": get_learnable_moves(evolved_data["id"], poke["level"])
                    })
                    self.queue_message(f"{old_name} évolue en {poke['name']} !")

                    if i == 0:
                        self.ally_id = poke["id"]
                        self.ally_name = poke["name"]
                        self.ally_max_hp = poke["stats"]["hp"]
                        self.ally_hp = self.ally_max_hp
                        self.bases, self.sprites, self.sprite_positions = load_combat_sprites(
                            self.ally_id, self.enemy_id
                        )

        self.hide_enemy_sprite = True

        valid_items = list_available_items()
        if len(valid_items) >= 2:
            self.message_queue.append(lambda: self.show_end_bonus(valid_items))


    def switch_pokemon(self, new_index):
        """
        Change le Pokémon actif avec un autre membre de l'équipe.

        Args:
            new_index (int): Index du nouveau Pokémon à envoyer au combat.
        """
        team = run_manager.get_team()

        if new_index != 0:
            team[0], team[new_index] = team[new_index], team[0]

        new_pokemon = team[0]
        self.ally_id = new_pokemon["id"]
        self.ally_name = new_pokemon["name"]
        self.ally_level = new_pokemon.get("level", 5)
        self.ally_hp = new_pokemon.get("hp", new_pokemon.get("stats", new_pokemon.get("base_stats"))["hp"])
        self.ally_max_hp = new_pokemon.get("stats", new_pokemon.get("base_stats"))["hp"]

        self.bases, self.sprites, self.sprite_positions = load_combat_sprites(self.ally_id, self.enemy_id)

        from ui.fight_menu import FightMenu
        self.fight_menu = FightMenu(
            self.bg,
            new_pokemon["moves"],
            pygame.font.Font("assets/fonts/power clear.ttf", 20),
            pygame.font.Font("assets/fonts/power clear bold.ttf", 18)
        )

        self.grid_pos = [0, 0]
        self.selected_index = 0
        self.state = "command"

        self.message_queue.append(self.enemy_turn)
        self.update_ally_xp()

    def throw_ball(self, ball_name):
        """
        Lance une Poké Ball en combat.

        Args:
            ball_name (str): Nom de la Ball utilisée.
        """
        if self.state != "command":
            return

        if "hp" not in self.enemy_data:
            self.enemy_data["hp"] = self.enemy_data["stats"]["hp"]

        self.capture_result = attempt_capture(
            self.enemy_data,
            ball_name,
            status=self.enemy_data.get("status")
        )
        self.capture_result["ball_used"] = ball_name

        from ui.ball_animation import BallAnimation
        self.ball_animation = BallAnimation(ball_type=ball_name, pos=(200, 400))

        self.state = "throwing_ball"

    def resolve_capture_result(self):
        """
        Applique les effets d'une tentative de capture après l’animation.
        """
        for msg in self.capture_result["messages"]:
            self.queue_message(msg)

        if self.capture_effect and not self.capture_result.get("success"):
            self.capture_effect.trigger_out()
            self.hide_enemy_sprite = False
        else:
            self.hide_enemy_sprite = True

        if self.capture_result.get("success"):
            added = run_manager.has_team_space()

            self.message_queue.append(lambda: self.handle_victory())

            if added:
                self.message_queue.append(lambda: run_manager.add_pokemon_to_team(self.enemy_data))
                self.message_queue.append(lambda: self.queue_message(f"{self.enemy_name} a rejoint votre équipe !"))
            else:
                self.message_queue.append(lambda: self.queue_message("Votre équipe est pleine, impossible de capturer ce Pokémon."))

        self.state = "command"

    def handle_event(self, event):
        """Gère tous les événements utilisateurs selon l’état actuel (combat, menu, messages, etc.)."""

        # === Pokémon Menu actif ===
        if self.pokemon_menu:
            self.pokemon_menu.handle_input(event)
            self.pokemon_menu.update(0)

            if self.pokemon_menu.closed:
                if self.pokemon_menu.option_chosen == "send":
                    selected_index = self.pokemon_menu.selected_index
                    selected_pokemon = self.pokemon_menu.get_selected_pokemon()

                    if selected_pokemon["id"] == self.ally_id:
                        self.queue_message(f"{selected_pokemon['name']} est déjà au combat.")
                    else:
                        self.queue_message(f"{selected_pokemon['name']} va être envoyé !")
                        self.switch_pokemon(selected_index)

                self.pokemon_menu = None
                self.state = "command"
                return

            if self.pokemon_menu.selection_active:
                return

        # === Messages texte animés ===
        if self.message_queue:
            current = self.message_queue[0]
            if isinstance(current, AnimatedText):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and current.done:
                    self.message_queue.pop(0)
                    while self.message_queue and not isinstance(self.message_queue[0], AnimatedText):
                        next_item = self.message_queue.pop(0)
                        try:
                            if callable(next_item):
                                next_item()
                        except Exception as e:
                            print(f"[handle_event] ❌ Erreur dans un callable : {e}")
                return

        # === Menu Bonus (post-victoire) ===
        if self.show_bonus and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.bonus_ui.move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self.bonus_ui.move_selection(1)
            elif event.key == pygame.K_RETURN:
                selected_item = self.bonus_ui.get_selected_item()
                if selected_item:
                    run_manager.add_item(selected_item)
                    self.manager.change_scene(BattleScene())  # Relance un nouveau combat
            return

        # === Menu Combat (attaques) ===
        if self.state == "fight_menu" and self.fight_menu:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_q):
                    self.fight_menu.move_cursor("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.fight_menu.move_cursor("right")
                elif event.key in (pygame.K_UP, pygame.K_z):
                    self.fight_menu.move_cursor("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.fight_menu.move_cursor("down")
                elif event.key == pygame.K_ESCAPE:
                    self.state = "command"
                    self.fight_menu = None
                elif event.key == pygame.K_RETURN:
                    selected_move = self.fight_menu.moves[self.fight_menu.selected_index]
                    self.use_move(selected_move)
            return

        # === Commandes principales (Combat, Pokémon, Sac, Fuite) ===
        if event.type == pygame.KEYDOWN:
            col, row = self.grid_pos
            if event.key in (pygame.K_UP, pygame.K_z) and row > 0:
                row -= 1
            elif event.key in (pygame.K_DOWN, pygame.K_s) and row < 1:
                row += 1
            elif event.key in (pygame.K_LEFT, pygame.K_q) and col > 0:
                col -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and col < 1:
                col += 1
            elif event.key == pygame.K_RETURN:
                self.selected_index = self.button_grid[col][row]

                if self.selected_index == 0:  # Combat
                    moves = run_manager.get_team()[0]["moves"]
                    self.fight_menu = FightMenu(
                        self.bg,
                        moves,
                        pygame.font.Font("assets/fonts/power clear.ttf", 20),
                        pygame.font.Font("assets/fonts/power clear bold.ttf", 18)
                    )
                    self.state = "fight_menu"

                elif self.selected_index == 1:  # Pokémon
                    team = run_manager.get_team()
                    if team:
                        self.pokemon_menu = PokemonMenu(team, current_ally_id=self.ally_id)
                        self.state = "pokemon_menu"
                    else:
                        self.queue_message("Vous n'avez aucun Pokémon.")

                elif self.selected_index == 2:  # Sac
                    from scene.bag_scene import BagScene
                    self.manager.change_scene(BagScene())

                elif self.selected_index == 3:  # Fuite
                    self.queue_message("Impossible de fuir !")

            self.grid_pos = [col, row]
            self.selected_index = self.button_grid[col][row]

    def on_enter(self):
        """Méthode appelée à l'entrée de la scène (non utilisée ici)."""
        pass

    def on_exit(self):
        """Méthode appelée à la sortie de la scène (non utilisée ici)."""
        pass

    def update(self, dt):
        """Met à jour tous les éléments dynamiques du combat (animations, effets, barres)."""
        if self.throw_animation:
            self.throw_animation.update(dt)

        if self.capture_effect:
            self.capture_effect.update(dt)

        if self.ball_animation:
            self.ball_animation.update(dt)
            if self.ball_animation.is_finished():
                self.ball_animation = None
                if self.capture_effect:
                    self.capture_effect.trigger_in()
                    self.hide_enemy_sprite = True
                ball_type = self.capture_result.get("ball_used", "Poké Ball")
                self.ball_throw = BallThrow(
                    ball_type=ball_type,
                    start_pos=(200, 400),
                    target_pos=(360, 130),
                    result=self.capture_result
                )

        if self.ball_throw:
            self.ball_throw.update(dt)
            if self.ball_throw.is_done():
                self.resolve_capture_result()
                self.ball_throw = None

        if self.sprites:
            for sprite in self.sprites:
                if hasattr(sprite, "update"):
                    sprite.update(dt)

        if self.pokemon_menu:
            self.pokemon_menu.update(dt)

        starter = run_manager.get_team()[0]
        self.ally_hp = starter.get("hp", starter["stats"]["hp"])
        self.ally_max_hp = starter["stats"]["hp"]

        self.update_ally_xp()

        if hasattr(self, "ally_xp_bar"):
            self.ally_xp_bar.update(self.ally_xp, dt / 1000)

        if hasattr(self, "ally_hp_bar"):
            self.ally_hp_bar.update(self.ally_hp, dt / 1000)

        if hasattr(self, "enemy_hp_bar"):
            self.enemy_hp_bar.update(self.enemy_hp, dt / 1000)

    def update_ally_xp(self):
        """
        Met à jour les valeurs d'XP du Pokémon actif.
        Calcule l'XP dans le niveau et les bornes du niveau.
        """
        starter = run_manager.get_team()[0]
        xp_total = starter.get("xp", 0)

        # Déduire le niveau réel
        level = 1
        while self.xp_required(level) <= xp_total:
            level += 1
        level -= 1

        starter["level"] = level
        self.ally_level = level

        xp_prev = self.xp_required(level)
        xp_next = self.xp_required(level + 1)
        xp_in_level = xp_total - xp_prev
        xp_needed = xp_next - xp_prev

        self.ally_xp = xp_in_level
        self.ally_max_xp = xp_needed

        if hasattr(self, "ally_xp_bar"):
            self.ally_xp_bar.max_xp = xp_needed
            self.ally_xp_bar.update(xp_in_level, 0)

    def queue_message_with_xp_update(self, text):
        """Met à jour la barre d’XP et ajoute un message dans la file."""
        self.update_ally_xp()
        self.queue_message(text)

    def draw(self, screen):
        """Affiche l’ensemble de la scène de combat : sprites, UI, menus, effets visuels."""
        sprites = list(self.sprites)
        if self.hide_enemy_sprite or (self.capture_effect and self.capture_effect.is_active()):
            sprites[1] = None

        self.update_ally_xp()

        draw_combat_scene(
            screen,
            self.bg,
            self.bases,
            sprites,
            positions=self.sprite_positions,
            ally_name=self.ally_name,
            enemy_name=self.enemy_name,
            ally_level=self.ally_level,
            enemy_level=self.enemy_level,
            enemy_gender=self.enemy_gender,
            draw_ally_hp_bar=False
        )

        if self.ally_xp_bar:
            self.ally_xp_bar.draw(screen)

        if self.ally_hp_bar:
            self.ally_hp_bar.draw(screen)
        if self.enemy_hp_bar:
            self.enemy_hp_bar.draw(screen)

        if self.pokemon_menu:
            self.pokemon_menu.draw(screen)
            return

        if self.state == "fight_menu" and self.fight_menu:
            self.fight_menu.surface = screen
            self.fight_menu.draw()
            return

        if self.capture_effect:
            self.capture_effect.draw(screen)
        if self.ball_animation:
            self.ball_animation.draw(screen)
        if self.throw_animation:
            self.throw_animation.draw(screen)
        if self.ball_throw:
            self.ball_throw.draw(screen)

        if self.message_queue:
            self.render_current_message(screen)
        elif self.show_bonus:
            self.render_bonus_message(screen)
            self.bonus_ui.draw(screen)
        elif self.state == "command":
            self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")
            for i, button in enumerate(self.buttons):
                button.draw(screen, selected=(i == self.selected_index))
        else:
            self.dialog_box.draw(screen, "", draw_box=True)

    def render_current_message(self, screen):
        """Affiche le message animé actuel dans la boîte de dialogue."""
        if not self.message_queue:
            return

        current = self.message_queue[0]

        if isinstance(current, AnimatedText):
            elapsed = (pygame.time.get_ticks() - current.start_time) / 1000
            chars_visible = min(int(elapsed * current.speed), len(current.full_text))
            text_to_display = current.full_text[:chars_visible]
            current.done = chars_visible == len(current.full_text)
            self.dialog_box.draw(screen, text_to_display)
        else:
            self.dialog_box.draw(screen, "", draw_box=True)

    def is_blocked(self):
        """Renvoie True si une action ou un message est encore en cours d’affichage."""
        if not self.message_queue:
            return False
        current = self.message_queue[0]
        if isinstance(current, AnimatedText):
            return not current.done
        return True

    def render_bonus_message(self, screen):
        """Affiche le message d’instructions pendant le choix du bonus (post-victoire)."""
        if not self.bonus_message:
            return
        elapsed = (pygame.time.get_ticks() - self.bonus_message.start_time) / 1000
        chars_visible = min(int(elapsed * self.bonus_message.speed), len(self.bonus_message.full_text))
        text_to_display = self.bonus_message.full_text[:chars_visible]
        self.dialog_box.draw(screen, text_to_display)
