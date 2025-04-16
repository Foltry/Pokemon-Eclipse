import pygame
from core.scene_manager import SceneManager
from scene.battle_scene import BattleScene  # ou StarterScene si tu veux

def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 384))
    pygame.display.set_caption("Pokémon Eclipse")
    clock = pygame.time.Clock()
    running = True

    scene_manager = SceneManager()
    scene_manager.change_scene(BattleScene())  # ou StarterScene()

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)  # <-- Ajout essentiel

        scene_manager.update(dt)
        scene_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
