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
from ui.attack_effects import AttackEffect
from ui.fight_menu import FightMenu

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
        if "moves" not in starter or not starter["moves"]:
            starter["moves"] = [
                {"name": "Flammèche", "type": "Feu", "pp": 15, "max_pp": 15},
                {"name": "Charge", "type": "Normal", "pp": 3, "max_pp": 20},
                {"name": "Griffe", "type": "Normal", "pp": 10, "max_pp": 20},
                {"name": "Exploforce", "type": "Combat", "pp": 0, "max_pp": 5},
            ]


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
        self.bonus_message = None
        self.attack_effect = None
        self.state = "command"
        self.fight_menu = None

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

        if self.attack_effect:
            self.attack_effect.update(dt)
            if not self.attack_effect.active:
                self.attack_effect = None

        if self.throw_animation:
            if not self.capture_started and self.throw_animation.has_landed():
                self.capture_effect.trigger_in()
                self.capture_started = True
                self.hide_enemy_sprite = True

            if self.capture_started and self.capture_effect.current_phase() is None and not self.capture_effect.is_active() and not self.waiting_out:
                pass

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

        if self.sprites:
            for sprite in self.sprites:
                if hasattr(sprite, "update"):
                    sprite.update(dt)

    def handle_event(self, event):
        # Priorité : gestion de la file de messages
        if self.message_queue:
            current = self.message_queue[0]
            if isinstance(current, AnimatedText):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and current.done:
                    self.message_queue.pop(0)
            elif callable(current):
                current()
                self.message_queue.pop(0)
            return

        # Priorité : gestion de la sélection des bonus
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

        # Gestion du FightMenu (nouveau système)
        if self.state == "fight_menu" and self.fight_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.fight_menu.move_cursor("left")
                elif event.key == pygame.K_RIGHT:
                    self.fight_menu.move_cursor("right")
                elif event.key == pygame.K_UP:
                    self.fight_menu.move_cursor("up")
                elif event.key == pygame.K_DOWN:
                    self.fight_menu.move_cursor("down")
                elif event.key == pygame.K_ESCAPE:
                    # Retour au menu de commande principal
                    self.state = "command"
                    self.fight_menu = None
                elif event.key == pygame.K_RETURN:
                    # TODO : ici tu pourras lancer l'attaque plus tard
                    selected_move = self.fight_menu.moves[self.fight_menu.selected_index]
                    self.queue_message(f"{self.ally_name} utilise {selected_move['name']} !")
                    self.state = "command"
                    self.fight_menu = None
            return

        # Gestion du menu de commande principal (Fight / Bag / Pokémon / Fuite)
        if event.type == pygame.KEYDOWN:
            col, row = self.grid_pos
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
                    # Ouvrir FightMenu correctement avec tous les arguments
                    moves = run_manager.get_team()[0]["moves"]
                    font_path = os.path.join("assets", "fonts", "power clear.ttf")
                    pp_font_path = os.path.join("assets", "fonts", "power clear bold.ttf")
                    fight_font = pygame.font.Font(font_path, 20)
                    pp_font = pygame.font.Font(pp_font_path, 18)

                    self.fight_menu = FightMenu(self.bg, moves, fight_font, pp_font)
                    self.state = "fight_menu"
                elif self.selected_index == 1:
                    self.queue_message("Ce menu n’est pas encore disponible.")
                elif self.selected_index == 2:
                    pass  # Plus tard pour Pokémon
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
        if len(valid_items) < 2:
            return
        self.bonus_options = random.sample(valid_items, 2)
        self.bonus_ui.set_items(self.bonus_options)
        self.show_bonus = True
        y = 300 + (85 - self.font.get_height()) // 2
        self.bonus_message = AnimatedText("Choisissez un objet :", self.font, (40, y), speed=50)

    def render_bonus_message(self, screen):
        if not self.bonus_message:
            return
        elapsed = (pygame.time.get_ticks() - self.bonus_message.start_time) / 1000
        nb_chars = min(int(elapsed * self.bonus_message.speed), len(self.bonus_message.full_text))
        visible = self.bonus_message.full_text[:nb_chars]
        self.dialog_box.draw(screen, visible)

    def draw(self, screen):
        sprites = list(self.sprites)
        if self.capture_effect and self.capture_effect.is_active():
            sprites[1] = None
        elif self.hide_enemy_sprite:
            sprites[1] = None

        # Fond + Pokémon + bases
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

        if self.state == "fight_menu":
            # ➡️ Si on est en fight_menu : on affiche le fond message.png à la place de la dialogue box
            message_bg = pygame.image.load("assets/ui/battle/message.png").convert_alpha()
            screen.blit(message_bg, (0, 288))
        else:
            # ➡️ Sinon, on affiche normalement la dialogue box
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

        # ➡️ Affiche les effets d'animation
        if self.capture_effect:
            self.capture_effect.draw(screen)
        if self.throw_animation:
            self.throw_animation.draw(screen)
        if self.attack_effect:
            self.attack_effect.draw(screen)

        # ➡️ FightMenu par-dessus tout
        if self.state == "fight_menu" and self.fight_menu:
            self.fight_menu.surface = screen
            self.fight_menu.draw()
