import os
import random
import pygame

from core.scene_manager import Scene
from core.run_manager import run_manager

from ui.battle_ui import load_battle_ui, load_combat_sprites, draw_combat_scene
from ui.bonus_ui import BonusUI
from ui.animated_text import AnimatedText
from ui.fight_menu import FightMenu
from ui.capture_effect import CaptureEffect
from ui.ballthrow import BallThrow
from ui.pokemon_menu import PokemonMenu

from battle.capture_handler import attempt_capture
from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves
from data.items_loader import list_available_items


class BattleScene(Scene):
    def __init__(self):
        # === UI ===
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.bonus_ui = BonusUI(pos=(300, 300), spacing=34)
        self.font = pygame.font.Font("assets/fonts/power green.ttf", 18)
        self.button_grid = [[0, 1], [2, 3]]

        # === State ===
        self.grid_pos = [0, 0]
        self.selected_index = 0
        self.state = "command"
        self.pending_move = None
        self.message_queue = []
        self.victory_handled = False
        self.show_bonus = False
        self.bonus_options = []
        self.bonus_message = None
        self.pokemon_menu = None

        # === Effects ===
        self.throw_animation = None
        self.capture_effect = None
        self.ball_throw = None
        self.capture_result = None
        self.hide_enemy_sprite = False
        self.ball_animation = None

        # === Normalisation des données de l'équipe ===
        for pkm in run_manager.get_team():
            pkm.setdefault("level", 5)
            pkm.setdefault("stats", pkm.get("base_stats", {}))
            pkm.setdefault("hp", pkm["stats"].get("hp", 20))
            if "moves" not in pkm or not pkm["moves"]:
                pkm["moves"] = get_learnable_moves(pkm["id"], pkm["level"])

        # === Ally Setup ===
        starter = run_manager.get_team()[0]
        self.ally_id = starter["id"]
        self.ally_name = starter["name"]
        self.ally_level = starter["level"]
        self.ally_hp = starter["hp"]
        self.ally_max_hp = starter["stats"]["hp"]
        self.ally_xp = starter.get("xp", 0)
        self.ally_max_xp = 100

        # === Enemy Setup ===
        self.enemy_id = 16
        self.enemy_level = 5
        self.enemy_gender = random.choice(["♂", "♀"])
        self.enemy_data = get_pokemon_by_id(self.enemy_id)
        self.enemy_data["moves"] = get_learnable_moves(self.enemy_id, self.enemy_level)
        self.enemy_name = self.enemy_data["name"]
        self.enemy_hp = self.enemy_max_hp = self.enemy_data["stats"]["hp"]
        self.enemy_base_exp = self.enemy_data.get("base_experience", 50)

        # === Sprites ===
        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)
        self.capture_effect = CaptureEffect(sprite=self.sprites[1], pos=(360, 130))
        self.fight_menu = None


    def enemy_turn(self):
        """Le Pokémon ennemi choisit un move et attaque."""
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

    def queue_message(self, text):
        """Ajoute un message à afficher, soit dans la boîte de dialogue normale, soit dans le menu Pokémon."""
        y = 300 + (85 - self.font.get_height()) // 2
        animated = AnimatedText(text, self.font, (40, y), speed=50)

        if self.pokemon_menu and not self.pokemon_menu.selection_active:
            self.pokemon_menu.override_text = text
        else:
            self.message_queue.append(animated)


    def use_move(self, move):
        """Prépare et affiche le lancement d'une attaque par l'allié."""
        starter = run_manager.get_team()[0]
        attacker = {
            "name": starter["name"],
            "level": starter.get("level", 5),
            "types": starter.get("types", []),
            "stats": starter.get("stats") or starter.get("base_stats")
        }
        defender = self.enemy_data
        if "hp" not in defender:
            defender["hp"] = defender["stats"]["hp"]

        self.pending_move = (attacker, defender, move)
        self.queue_message(f"{attacker['name']} utilise {move['name']} !")
        self.state = "waiting_move"
        self.fight_menu = None

    def resolve_move(self):
        """Exécute le move préparé et gère les conséquences (HP, victoire, etc.)."""
        from battle.move_handler import use_move as core_use_move
        attacker, defender, move = self.pending_move
        result = core_use_move(attacker, defender, move)

        for message in result["messages"]:
            self.queue_message(message)

        self.ally_hp = attacker["stats"]["hp"]
        self.enemy_hp = defender["hp"]

        self.pending_move = None
        self.state = "command"

        if defender["hp"] <= 0:
            self.message_queue.append(self.handle_victory)
        else:
            # 👉 Tour de l'ennemi s'il est vivant
            self.message_queue.append(self.enemy_turn)


    def handle_victory(self):
        """Gère l'expérience gagnée et déclenche l'écran bonus (si dispo)."""
        self.victory_handled = True
        xp_gain = int((self.enemy_base_exp * self.enemy_level) / 7)
        for poke in run_manager.get_team():
            poke["xp"] = poke.get("xp", 0) + xp_gain

        valid_items = list_available_items()
        if len(valid_items) >= 2:
            self.bonus_options = random.sample(valid_items, 2)
            self.bonus_ui.set_items(self.bonus_options)
            self.show_bonus = True
            y = 300 + (85 - self.font.get_height()) // 2
            self.bonus_message = AnimatedText("Choisissez un objet :", self.font, (40, y), speed=50)

    def switch_pokemon(self, new_index):
        """Change de Pokémon actif et met à jour l'UI et les menus."""
        team = run_manager.get_team()

        if new_index != 0:
            team[0], team[new_index] = team[new_index], team[0]

        new_pokemon = team[0]
        self.ally_id = new_pokemon["id"]
        self.ally_name = new_pokemon["name"]
        self.ally_level = new_pokemon.get("level", 5)
        self.ally_hp = new_pokemon.get("hp", new_pokemon.get("stats", new_pokemon.get("base_stats"))["hp"])
        self.ally_max_hp = new_pokemon.get("stats", new_pokemon.get("base_stats"))["hp"]
        self.ally_xp = new_pokemon.get("xp", 0)

        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)

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

        # 👉 Tour de l'ennemi après changement de Pokémon
        self.message_queue.append(self.enemy_turn)


    def throw_ball(self, ball_name):
        """Prépare l'animation de lancer de Pokéball."""
        if self.state != "command":
            return

        # Normalisation des PV du Pokémon adverse
        if "hp" not in self.enemy_data:
            self.enemy_data["hp"] = self.enemy_data["stats"]["hp"]

        # Calcul du résultat de capture
        self.capture_result = attempt_capture(self.enemy_data, ball_name, status=self.enemy_data.get("status"))
        self.capture_result["ball_used"] = ball_name

        # Étape 1 : animation de la Pokéball qui vole (BallAnimation)
        from ui.ball_animation import BallAnimation
        self.ball_animation = BallAnimation(ball_type=ball_name, pos=(200, 400))  # ← Correction

        self.state = "throwing_ball"

    def resolve_capture_result(self):
        """Gère l'issue de la capture après animation de la Pokéball."""
        for msg in self.capture_result["messages"]:
            self.queue_message(msg)

        # Faire réapparaître le Pokémon (effet visuel inverse)
        if self.capture_effect:
            self.capture_effect.trigger_out()
            self.hide_enemy_sprite = False  # Réactive le sprite ennemi

        # Si le Pokémon est capturé
        if self.capture_result.get("success"):
            if run_manager.has_team_space():
                run_manager.add_pokemon_to_team(self.enemy_data)
                self.queue_message(f"{self.enemy_name} a rejoint votre équipe !")
            else:
                self.queue_message("Votre équipe est pleine, impossible de capturer ce Pokémon.")

        # Retour au combat après les messages
        self.message_queue.append(lambda: self.manager.change_scene(BattleScene()))
        self.state = "command"


    def handle_event(self, event):
        """Gère tous les événements utilisateurs selon l’état actuel (combat, menu, messages, etc.)."""

        # === Pokémon Menu actif ===
        if self.pokemon_menu:
            self.pokemon_menu.handle_input(event)
            self.pokemon_menu.update(0)  # Optionnel : animation frame

            if self.pokemon_menu.closed:
                if self.pokemon_menu.option_chosen == "send":
                    selected_index = self.pokemon_menu.selected_index
                    selected_pokemon = self.pokemon_menu.get_selected_pokemon()

                    if selected_pokemon["id"] == self.ally_id:
                        self.queue_message(f"{selected_pokemon['name']} est déjà au combat.")
                    else:
                        self.queue_message(f"{selected_pokemon['name']} va être envoyé !")
                        self.switch_pokemon(selected_index)

                # Fermeture du menu après traitement
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
                    if not self.message_queue and self.pending_move:
                        self.resolve_move()
                return
            elif callable(current):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current()
                    self.message_queue.pop(0)
                    if not self.message_queue and self.pending_move:
                        self.resolve_move()
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
                    self.manager.change_scene(BattleScene())
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
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        """Mise à jour des éléments dynamiques (animations, effets, menus)."""
        if self.throw_animation:
            self.throw_animation.update(dt)

        if self.capture_effect:
            self.capture_effect.update(dt)

        # Étape 1 : animation préliminaire (BallAnimation)
        if self.ball_animation:
            self.ball_animation.update(dt)
            if self.ball_animation.is_finished():
                self.ball_animation = None

                # Effet de disparition du Pokémon
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

        # Étape 2 : lancer réel avec BallThrow
        if self.ball_throw:
            self.ball_throw.update(dt)
            if self.ball_throw.is_done():
                self.resolve_capture_result()
                self.ball_throw = None

        # MAJ des sprites
        if self.sprites:
            for sprite in self.sprites:
                if hasattr(sprite, "update"):
                    sprite.update(dt)

        if self.pokemon_menu:
            self.pokemon_menu.update(dt)

    def draw(self, screen):
        """Affiche toute la scène de combat : arrière-plan, sprites, menus, effets, etc."""

        # === Préparation des sprites ===
        sprites = list(self.sprites)
        if self.hide_enemy_sprite or (self.capture_effect and self.capture_effect.is_active()):
            sprites[1] = None  # Cache le sprite ennemi si nécessaire

        # === Affichage de la scène principale ===
        draw_combat_scene(
            screen, self.bg, self.bases, sprites,
            ally_name=self.ally_name,
            enemy_name=self.enemy_name,
            ally_hp=self.ally_hp, ally_max_hp=self.ally_max_hp,
            enemy_hp=self.enemy_hp, enemy_max_hp=self.enemy_max_hp,
            ally_level=self.ally_level, enemy_level=self.enemy_level,
            enemy_gender=self.enemy_gender,
            ally_xp=self.ally_xp, ally_max_xp=self.ally_max_xp
        )

        # === Menu Pokémon ===
        if self.pokemon_menu:
            self.pokemon_menu.draw(screen)
            return  # Priorité absolue : on affiche uniquement le menu Pokémon

        # === Menu Combat (attaques) ===
        if self.state == "fight_menu" and self.fight_menu:
            self.fight_menu.surface = screen
            self.fight_menu.draw()
            return

        # === Boîte de dialogue principale ===
        self.dialog_box.draw(screen, "", draw_box=True)

        # === Message animé ou bonus ===
        if self.message_queue:
            self.render_current_message(screen)
        elif self.show_bonus:
            self.render_bonus_message(screen)
            self.bonus_ui.draw(screen)
        elif self.state != "throwing_ball" and not self.ball_animation and not self.ball_throw:
            # Affichage normal si aucune animation de capture
            self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")
            for i, button in enumerate(self.buttons):
                button.draw(screen, selected=(i == self.selected_index))

        # === Effets visuels ===
        if self.capture_effect:
            self.capture_effect.draw(screen)
        if self.ball_animation:
            self.ball_animation.draw(screen)
        if self.throw_animation:
            self.throw_animation.draw(screen)
        if self.ball_throw:
            self.ball_throw.draw(screen)

    def render_current_message(self, screen):
        """Affiche le message animé en cours, caractère par caractère."""
        if not self.message_queue:
            return

        current = self.message_queue[0]
        if isinstance(current, AnimatedText):
            elapsed = (pygame.time.get_ticks() - current.start_time) / 1000
            chars_visible = min(int(elapsed * current.speed), len(current.full_text))
            text_to_display = current.full_text[:chars_visible]
            current.done = chars_visible == len(current.full_text)
            self.dialog_box.draw(screen, text_to_display)

    def render_bonus_message(self, screen):
        """Affiche le message d'instructions pour le choix de bonus (après victoire)."""
        if not self.bonus_message:
            return

        elapsed = (pygame.time.get_ticks() - self.bonus_message.start_time) / 1000
        chars_visible = min(int(elapsed * self.bonus_message.speed), len(self.bonus_message.full_text))
        text_to_display = self.bonus_message.full_text[:chars_visible]
        self.dialog_box.draw(screen, text_to_display)
