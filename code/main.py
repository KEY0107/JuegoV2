import pygame
from settings import FPS  # Asegúrate de tener definidos los parámetros necesarios


def main():
    pygame.init()
    pygame.mixer.init()

    # Obtener la resolución actual del monitor
    display_info = pygame.display.Info()
    screen_width, screen_height = display_info.current_w, display_info.current_h

    # Crear la ventana en modo RESIZABLE, inicializada al tamaño del monitor
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("El Umbral del Olvido")

    # Aquí puedes llamar a tu pantalla de inicio o al capítulo
    from home_screen import start_screen

    start_screen(screen)

    # capitulo 1
    from chapter1 import run_chapter1

    run_chapter1(screen)

    pygame.quit()


if __name__ == "__main__":
    main()
