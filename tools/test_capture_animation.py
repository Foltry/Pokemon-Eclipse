import os
import sys
import pygame
import json
import gif_pygame

# Ajout du chemin du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.capture_effect import CaptureEffect
from ui.ballthrow import BallThrow
from ui.battle_ui import resize_gif, get_gif_max_size

pygame.init()
screen = pygame.display.set_mode((512, 320))
pygame.display.set_caption("Test Capture Animation")
clock = pygame.time.Clock()

# === Chargement des données de Roucool ===
with open("data/pokemon.json", encoding="utf-8") as f:
    pokemons = json.load(f)
roucool = next(p for p in pokemons if p["id"] == 16)

# === Chargement et redimensionnement du sprite ===
sprite_path = os.path.join("assets/sprites/pokemon", roucool["sprites"]["front"])
gif = gif_pygame.load(sprite_path)
sprite_size = get_gif_max_size(sprite_path)
sprite = resize_gif(gif, sprite_size)

# === Création des animations ===
capture_effect = CaptureEffect(sprite, pos=(340, 90))
result = {"success": False, "shakes": 3, "messages": [f"{roucool['name']} s'est échappé !"]}
ball_throw = BallThrow("superball", start_pos=(462, 240), target_pos=(300, 120), result=result)

# === État de contrôle ===
running = True
frame_count = 0
capture_started = False
waiting_out = False
message_shown = False
hide_sprite = False  # 👈 Pour cacher le sprite au bon moment

while running:
    dt = clock.tick(60)
    screen.fill((80, 160, 80))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update animations
    ball_throw.update(dt)
    capture_effect.update(dt)

    # Log de débogage détaillé
    print(f"[{frame_count}] Phase: {ball_throw.phase}, Shakes: {ball_throw.shake_index}/{ball_throw.shakes}, capture_effect: active={capture_effect.is_active()}, out_started={waiting_out}, in_started={capture_started}, in_done={capture_started and not capture_effect.is_active()}")
    frame_count += 1

    # Déclenche capture_in à l'atterrissage
    if not capture_started and ball_throw.has_landed():
        print(f"[{frame_count}] [ACTION] trigger_in()")
        capture_effect.trigger_in()
        capture_started = True
        hide_sprite = True

    # Fin de l’effet capture_in → début des secousses
    if capture_started and capture_effect.current_phase() is None and not capture_effect.is_active() and not waiting_out:
        print(f"[{frame_count}] [INFO] capture_in terminé")
        print(f"[{frame_count}] [ACTION] début des secousses")

    # Déclenche capture_out après shake si la capture a échoué
    if capture_started and ball_throw.is_done() and not result["success"] and not waiting_out:
        print(f"[{frame_count}] [ACTION] trigger_out()")
        capture_effect.trigger_out()
        waiting_out = True

    # Une fois l’animation capture_out terminée
    if waiting_out and not capture_effect.is_active() and not message_shown:
        print(f"[{frame_count}] [MESSAGE] {result['messages'][0]}")
        message_shown = True
        hide_sprite = False  # ✅ On peut réafficher le Pokémon échappé

    # Affichage
    if capture_effect.is_active():
        capture_effect.draw(screen)
    elif not hide_sprite:
        screen.blit(sprite.blit_ready(), (340, 90))

    ball_throw.draw(screen)
    pygame.display.flip()

pygame.quit()
