import pygame
import json
import os
import random

from ui.battle_ui import load_battle_ui, load_combat_sprites, draw_combat_scene
from core.scene_manager import Scene
from core.run_manager import run_manager
from ui.bonus_ui import BonusUI
from ui.animated_text import AnimatedText
from ui.ballthrow import BallThrow
from ui.capture_effect import CaptureEffect
from battle.item_handler import use_item_on_pokemon
from battle.engine import calculate_damage

class BattleScene(Scene):
    def __init__(self):
        self.bg, self.dialog_box, self.buttons = load_battle_ui()
        self.bonus_ui = BonusUI(pos=(300, 300), spacing=34)
        self.button_grid = [[0, 1], [2, 3]]
        self.grid_pos = [0, 0]
        self.selected_index = self.button_grid[0][0]
        self.victory_handled = False
        self.show_bonus = False
        self.bonus_options = []
        self.message_queue = []
        self.font = pygame.font.Font("assets/fonts/power green.ttf", 18)

        self.throw_animation = None
        self.throw_result = None
        self.capture_effect = None

        self.capture_started = False
        self.waiting_out = False
        self.message_shown = False
        self.hide_enemy_sprite = False

        starter = run_manager.get_team()[0]
        self.ally_id = starter["id"]
        self.ally_name = starter["name"]
        self.ally_level = starter.get("level", 5)
        stats = starter.get("stats") or starter.get("base_stats")
        self.ally_hp = self.ally_max_hp = stats["hp"]
        self.ally_xp = starter.get("xp", 0)
        self.ally_max_xp = 100

        self.enemy_id = 16
        self.enemy_level = 5
        self.enemy_gender = random.choice(["♂", "♀"])

        with open("data/pokemon.json", encoding="utf-8") as f:
            data = json.load(f)
            self.enemy_data = next((p for p in data if p["id"] == int(self.enemy_id)), None)

        self.enemy_name = self.enemy_data["name"]
        self.enemy_hp = self.enemy_max_hp = self.enemy_data["stats"]["hp"]
        self.enemy_base_exp = self.enemy_data.get("base_experience", 50)

        self.bases, self.sprites = load_combat_sprites(self.ally_id, self.enemy_id)
        self.capture_effect = CaptureEffect(sprite=self.sprites[1], pos=(360, 130))

    def get_ally_stats(self):
        return run_manager.get_team()[0].get("stats") or run_manager.get_team()[0].get("base_stats")

    def queue_message(self, text):
        y = 300 + (85 - self.font.get_height()) // 2
        self.message_queue.append(AnimatedText(text, self.font, (40, y), speed=50))

    def render_current_message(self, screen):
        current = self.message_queue[0]
        if isinstance(current, AnimatedText):
            elapsed = (pygame.time.get_ticks() - current.start_time) / 1000
            nb_chars = min(int(elapsed * current.speed), len(current.full_text))
            visible = current.full_text[:nb_chars]
            current.done = nb_chars == len(current.full_text)
            self.dialog_box.draw(screen, visible)
        elif callable(current):
            self.dialog_box.draw(screen, "")

    def on_enter(self): pass
    def on_exit(self): pass

    def update(self, dt):
        if self.throw_animation:
            self.throw_animation.update(dt)
        if self.capture_effect:
            self.capture_effect.update(dt)

        if self.throw_animation:
            if not self.capture_started and self.throw_animation.has_landed():
                self.capture_effect.trigger_in()
                self.capture_started = True
                self.hide_enemy_sprite = True

            if self.capture_started and self.capture_effect.current_phase() is None and not self.capture_effect.is_active() and not self.waiting_out:
                pass  # capture_in terminé, aucun log

            if self.capture_started and self.throw_animation.is_done() and not self.throw_result["success"] and not self.waiting_out:
                self.capture_effect.trigger_out()
                self.waiting_out = True

            if self.waiting_out and not self.capture_effect.is_active() and not self.message_shown:
                self.resolve_capture_result()
                self.message_shown = True
                self.hide_enemy_sprite = False

            if self.capture_started and self.throw_animation.is_done() and self.throw_result["success"] and not self.message_shown:
                self.resolve_capture_result()
                self.message_shown = True
                self.hide_enemy_sprite = False

            if self.message_shown and not self.capture_effect.is_active():
                self.throw_animation = None


    def handle_event(self, event):
        if self.message_queue:
            current = self.message_queue[0]
            if isinstance(current, AnimatedText):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and current.done:
                    self.message_queue.pop(0)
            elif callable(current):
                current()
                self.message_queue.pop(0)
            return

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

        if event.type == pygame.KEYDOWN:
            col, row = self.grid_pos
            if event.key == pygame.K_UP and row > 0: row -= 1
            elif event.key == pygame.K_DOWN and row < 1: row += 1
            elif event.key == pygame.K_LEFT and col > 0: col -= 1
            elif event.key == pygame.K_RIGHT and col < 1: col += 1
            elif event.key == pygame.K_RETURN:
                self.selected_index = self.button_grid[col][row]

                if self.selected_index == 0:
                    move = {"name": "Charge", "power": 40, "type": "normal", "damage_class": "physical"}
                    attacker = {"name": self.ally_name, "level": self.ally_level, "stats": self.get_ally_stats(), "types": run_manager.get_team()[0]["types"]}
                    defender = {"name": self.enemy_name, "level": self.enemy_level, "stats": self.enemy_data["stats"], "types": self.enemy_data["types"]}
                    damage, is_crit, multiplier = calculate_damage(attacker, defender, move)
                    self.queue_message(f"{attacker['name']} utilise {move['name']} !")
                    if is_crit: self.queue_message("Coup critique !")
                    if multiplier > 1: self.queue_message("C’est super efficace !")
                    elif 0 < multiplier < 1: self.queue_message("Ce n’est pas très efficace...")
                    self.queue_message(f"{defender['name']} perd {damage} PV !")

                    def apply_damage():
                        self.enemy_hp = max(0, self.enemy_hp - damage)
                        if self.enemy_hp == 0 and not self.victory_handled:
                            self.handle_victory()
                    self.message_queue.append(apply_damage)

                elif self.selected_index == 2:
                    self.enemy_data["hp"] = self.enemy_hp
                    self.enemy_data["stats"]["max_hp"] = self.enemy_max_hp
                    result = use_item_on_pokemon("Super Ball", self.enemy_data)

                    self.throw_result = result
                    self.throw_animation = BallThrow(
                        ball_type="superball",
                        start_pos=(462, 240),
                        target_pos=(360, 130),
                        result=result
                    )

                    # Reset états capture
                    self.capture_started = False
                    self.waiting_out = False
                    self.message_shown = False
                    self.hide_enemy_sprite = False

                elif self.selected_index == 3:
                    self.manager.change_scene(BattleScene())

            self.grid_pos = [col, row]
            self.selected_index = self.button_grid[col][row]

    def resolve_capture_result(self):
        result = self.throw_result
        for msg in result["messages"]:
            self.queue_message(msg)

        if result["success"]:
            run_manager.add_pokemon_to_team(self.enemy_data)
            self.queue_message(f"{self.enemy_name} a rejoint votre équipe !")
            self.message_queue.append(lambda: self.manager.change_scene(BattleScene()))

    def handle_victory(self):
        self.victory_handled = True
        xp_gain = int((self.enemy_base_exp * self.enemy_level) / 7)
        for poke in run_manager.get_team():
            poke["xp"] = poke.get("xp", 0) + xp_gain
        with open("data/items.json", encoding="utf-8") as f:
            items = json.load(f)
        valid_items = [item["name"] for item in items if item["name"].lower() != "master ball" and "sprite" in item]
        if len(valid_items) < 2: return
        self.bonus_options = random.sample(valid_items, 2)
        self.bonus_ui.set_items(self.bonus_options)
        self.show_bonus = True

    def draw(self, screen):
        sprites = list(self.sprites)
        if self.capture_effect and self.capture_effect.is_active():
            sprites[1] = None
        elif self.hide_enemy_sprite:
            sprites[1] = None

        draw_combat_scene(
            screen,
            self.bg,
            self.bases,
            sprites,
            ally_name=self.ally_name,
            enemy_name=self.enemy_name,
            ally_hp=self.ally_hp,
            ally_max_hp=self.ally_max_hp,
            enemy_hp=self.enemy_hp,
            enemy_max_hp=self.enemy_max_hp,
            ally_level=self.ally_level,
            enemy_level=self.enemy_level,
            enemy_gender=self.enemy_gender,
            ally_xp=self.ally_xp,
            ally_max_xp=self.ally_max_xp
        )

        if self.capture_effect:
            self.capture_effect.draw(screen)
        if self.throw_animation:
            self.throw_animation.draw(screen)

        if self.message_queue:
            self.render_current_message(screen)
        elif self.show_bonus:
            self.dialog_box.draw(screen, "Choisissez un objet :")
            self.bonus_ui.draw(screen)
        else:
            self.dialog_box.draw(screen, f"Que doit faire {self.ally_name} ?")
            for i, button in enumerate(self.buttons):
                button.draw(screen, selected=(i == self.selected_index))
