# death.py
import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def death_screen(screen):
    font_large = pygame.font.SysFont("arial", 48, bold=True)
    font_small = pygame.font.SysFont("arial", 36)

    while True:
        screen.fill((0, 0, 0))
        text_dead = font_large.render("¡Estás muerto!", True, (255, 0, 0))
        text_restart = font_small.render("Presiona R para reiniciar", True, (255, 255, 255))

        screen.blit(text_dead, ((SCREEN_WIDTH - text_dead.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text_restart, ((SCREEN_WIDTH - text_restart.get_width()) // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # <- Aquí indica que se debe reiniciar el juego
