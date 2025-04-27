# scene/battle_scene.py

import os
import random
import pygame

from core.scene_manager import Scene
from core.run_manager import run_manager

from ui.battle_ui import load_battle_ui, load_combat_sprites, draw_combat_scene
from ui.bonus_ui import BonusUI
from ui.animated_text import AnimatedText
from ui.attack_effects import AttackEffect
from ui.fight_menu import FightMenu
from ui.capture_effect import CaptureEffect
from ui.ballthrow import BallThrow

from battle.engine import calculate_damage
from battle.item_handler import use_item_on_pokemon
from battle.capture_handler import attempt_capture

from data.pokemon_loader import get_pokemon_by_id, get_learnable_moves
from data.items_loader import list_available_items


class BattleScene(Scene):
    def __init__(self):
        # --- Assets & UI ---
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.bonus_ui = BonusUI(pos=(300, 300), spacing=34)
        self.font = pygame.font.Font("assets/fonts/power green.ttf", 18)

        # --- Combat State ---
        self.button_grid = [[0, 1], [2, 3]]
        self.grid_pos = [0, 0]
        self.selected_index = 0
        self.state = "command"
        self.pending_move = None
        self.message_queue = []
        self.show_bonus = False
        self.bonus_options = []
        self.bonus_message = None
        self.victory_handled = False

        # --- Sprites & Effects ---
        self.throw_animation = None
        self.capture_effect = None
        self.attack_effect = None
        self.ball_throw = None
        self.capture_result = None
        self.hide_enemy_sprite = False

        # --- Team (Ally) ---
        starter = run_manager.get_team()[0]
        if "moves" not in starter or not starter["moves"]:
            starter["moves"] = get_learnable_moves(starter["id"], starter.get("level", 5))
        self.ally_id = starter["id"]
        self.ally_name = starter["name"]
        self.ally_level = starter.get("level", 5)
        self.ally_hp = self.ally_max_hp = starter.get("stats", starter.get("base_stats"))["hp"]
        self.ally_xp = starter.get("xp", 0)
        self.ally_max_xp = 100

        # --- Opponent (Enemy) ---
        self.enemy_id = 16
        self.enemy_level = 5
        self.enemy_gender = random.choice(["♂", "♀"])
        self.enemy_data = get_pokemon_by_id(self.enemy_id)
        self.enemy_data["moves"] = get_learnable_moves(self.enemy_id, self.enemy_level)
        self.enemy_name = self.enemy_data["name"]
        self.enemy_hp = self.enemy_max_hp = self.enemy_data["stats"]["hp"]
        self.enemy_base_exp = self.enemy_data.get("base_experience", 50)

        # --- Sprites ---
        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)
        self.capture_effect = CaptureEffect(sprite=self.sprites[1], pos=(360, 130))

        # --- Fight Menu ---
        self.fight_menu = None

    # ======================================================
    # Combat Core
    # ======================================================

    def queue_message(self, text):
        y = 300 + (85 - self.font.get_height()) // 2
        self.message_queue.append(AnimatedText(text, self.font, (40, y), speed=50))

    def use_move(self, move):
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
        from battle.move_handler import use_move as core_use_move
        attacker, defender, move = self.pending_move
        result = core_use_move(attacker, defender, move)

        for message in result["messages"]:
            self.queue_message(message)

        self.ally_hp = attacker["stats"]["hp"]
        self.enemy_hp = defender["hp"]

        if defender["hp"] <= 0:
            self.message_queue.append(self.handle_victory)

        self.pending_move = None
        self.state = "command"

    def handle_victory(self):
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

    # ======================================================
    # Capture Management
    # ======================================================

    def throw_ball(self, ball_name):
        """Tente une capture et lance l'animation BallThrow."""
        if self.state != "command":
            return

        self.capture_result = attempt_capture(self.enemy_data, ball_name, status=self.enemy_data.get("status"))
        self.ball_throw = BallThrow(
            ball_type=ball_name,
            start_pos=(200, 400),
            target_pos=(360, 130),
            result=self.capture_result
        )

        self.state = "throwing_ball"

    def resolve_capture_result(self):
        """Traite la fin d'une tentative de capture."""
        for msg in self.capture_result["messages"]:
            self.queue_message(msg)

        if self.capture_result.get("success"):
            if run_manager.has_team_space():
                run_manager.add_pokemon_to_team(self.enemy_data)
                self.queue_message(f"{self.enemy_name} a rejoint votre équipe !")
            else:
                self.queue_message("Votre équipe est pleine, impossible de capturer ce Pokémon.")

        self.message_queue.append(lambda: self.manager.change_scene(BattleScene()))
        self.state = "command"


    # ======================================================
    # Events
    # ======================================================

    def handle_event(self, event):
        # --- Gestion messages en file ---
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

        # --- Gestion Bonus UI après victoire ---
        if self.show_bonus:
            if event.type == pygame.KEYDOWN:
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

        # --- Gestion Fight Menu ---
        if self.state == "fight_menu" and self.fight_menu:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    self.fight_menu.handle_navigation(event.key)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "command"
                    self.fight_menu = None
                elif event.key == pygame.K_RETURN:
                    selected_move = self.fight_menu.moves[self.fight_menu.selected_index]
                    self.use_move(selected_move)
            return

        # --- Gestion Sélection principale (Command Menu) ---
        if event.type == pygame.KEYDOWN:
            col, row = self.grid_pos

            # Navigation curseur
            if event.key == pygame.K_UP and row > 0:
                row -= 1
            elif event.key == pygame.K_DOWN and row < 1:
                row += 1
            elif event.key == pygame.K_LEFT and col > 0:
                col -= 1
            elif event.key == pygame.K_RIGHT and col < 1:
                col += 1

            elif event.key == pygame.K_RETURN:
                self.selected_index = self.button_grid[col][row]

                if self.selected_index == 0:
                    # Fight
                    moves = run_manager.get_team()[0]["moves"]
                    font_path = os.path.join("assets/fonts", "power clear.ttf")
                    pp_font_path = os.path.join("assets/fonts", "power clear bold.ttf")
                    self.fight_menu = FightMenu(
                        self.bg,
                        moves,
                        pygame.font.Font(font_path, 20),
                        pygame.font.Font(pp_font_path, 18)
                    )
                    self.state = "fight_menu"

                elif self.selected_index == 1:
                    # Pokémon (non dispo)
                    self.queue_message("Changer de Pokémon n'est pas disponible.")

                elif self.selected_index == 2:
                    # Bag
                    from scene.bag_scene import BagScene
                    self.manager.change_scene(BagScene())

                elif self.selected_index == 3:
                    # Run
                    self.manager.change_scene(BattleScene())

            self.grid_pos = [col, row]
            self.selected_index = self.button_grid[col][row]


    def on_enter(self): pass
    def on_exit(self): pass

    def update(self, dt):
        if self.throw_animation:
            self.throw_animation.update(dt)
        if self.capture_effect:
            self.capture_effect.update(dt)
        if self.attack_effect:
            self.attack_effect.update(dt)
            if not self.attack_effect.active:
                self.attack_effect = None
        if self.ball_throw:
            self.ball_throw.update(dt)
            if self.ball_throw.is_done():
                self.resolve_capture_result()
                self.ball_throw = None

        if self.sprites:
            for sprite in self.sprites:
                if hasattr(sprite, "update"):
                    sprite.update(dt)

    def draw(self, screen):
        # Combat Scene
        sprites = list(self.sprites)
        if self.capture_effect and self.capture_effect.is_active():
            sprites[1] = None
        elif self.hide_enemy_sprite:
            sprites[1] = None

        draw_combat_scene(
            screen, self.bg, self.bases, sprites,
            ally_name=self.ally_name, enemy_name=self.enemy_name,
            ally_hp=self.ally_hp, ally_max_hp=self.ally_max_hp,
            enemy_hp=self.enemy_hp, enemy_max_hp=self.enemy_max_hp,
            ally_level=self.ally_level, enemy_level=self.enemy_level,
            enemy_gender=self.enemy_gender,
            ally_xp=self.ally_xp, ally_max_xp=self.ally_max_xp
        )

        # UI Layer
        if self.state == "fight_menu" and self.fight_menu:
            self.fight_menu.surface = screen
            self.fight_menu.draw()
        else:
            self.dialog_box.draw(screen, "", draw_box=True)
            if self.message_queue:
                self.render_current_message(screen)
            elif self.show_bonus:
                self.render_bonus_message(screen)
                self.bonus_ui.draw(screen)
            else:
                self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")
                for i, button in enumerate(self.buttons):
                    button.draw(screen, selected=(i == self.selected_index))

        # Effects
        if self.capture_effect:
            self.capture_effect.draw(screen)
        if self.throw_animation:
            self.throw_animation.draw(screen)
        if self.attack_effect:
            self.attack_effect.draw(screen)

    def render_current_message(self, screen):
        if not self.message_queue:
            return
        current = self.message_queue[0]
        if isinstance(current, AnimatedText):
            elapsed = (pygame.time.get_ticks() - current.start_time) / 1000
            nb_chars = min(int(elapsed * current.speed), len(current.full_text))
            visible = current.full_text[:nb_chars]
            current.done = nb_chars == len(current.full_text)
            self.dialog_box.draw(screen, visible)

    def render_bonus_message(self, screen):
        if not self.bonus_message:
            return
        elapsed = (pygame.time.get_ticks() - self.bonus_message.start_time) / 1000
        nb_chars = min(int(elapsed * self.bonus_message.speed), len(self.bonus_message.full_text))
        visible = self.bonus_message.full_text[:nb_chars]
        self.dialog_box.draw(screen, visible)
