import pygame
import sys
from scenes_chapter_2.scene import Scene

class FinCapitulo2Scene(Scene):
    def __init__(self, screen, player=None):
        super().__init__(screen)
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)  # Fuente estándar
        self.text = "Fin Capítulo 2"
        self.text_color = (255, 255, 255)  # Color blanco
        self.player = player if player else None  # Si necesitas usar al jugador
        self.start_time = pygame.time.get_ticks()  # Tiempo de inicio

    def handle_events(self, events):
        # Si el jugador presiona alguna tecla, se finaliza la escena inmediatamente
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.transition_to_chapter3()

    def update(self, dt):
        # Si han pasado 3 segundos, se transiciona automáticamente a chapter 3
        if pygame.time.get_ticks() - self.start_time >= 3000:
            self.transition_to_chapter3()

    def render(self):
        # Rellenamos la pantalla de negro
        self.screen.fill((0, 0, 0))
        # Creamos la superficie de texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        # Dibujamos el texto en la pantalla
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def transition_to_chapter3(self):
        # Aquí se realiza la transición al capítulo 3.
        # Por ejemplo, importando y llamando a la función que inicia chapter 3.
        try:
            from chapter3 import run_chapter3  # Asegúrate de que este módulo y función existen
            run_chapter3(self.screen)
        except Exception as e:
            print("Error al transicionar a chapter 3:", e)
            pygame.quit()
            sys.exit()
