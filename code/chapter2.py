import pygame
import sys
from scenes_chapter_2.cuarto_scene import CuartoScene
from scenes_chapter_2.sala_scene import SalaScene
from scenes_chapter_2.banio_scene import BanioScene
from scenes_chapter_2.calle_scene import CalleScene
from scenes_chapter_2.entrada_noche_scene import EntradaNocheScene
from scenes_chapter_2.cafeteria_scene import CafeteriaScene
from scenes_chapter_2.jardineras_noche import JardinerasNocheScene
from scenes_chapter_2.interior_cafeteria import InteriorCafeteriaScene
from scenes_chapter_2.interior_edificio_h_scene import InteriorEdificioHScene
from scenes_chapter_2.interior_edificio_h2_scene import InteriorEdificioH2Scene
from scenes_chapter_2.interior_edificio_i_scene import InteriorEdificioI
from scenes_chapter_2.interior_edificio_i2_scene import InteriorEdificioI2
from scenes_chapter_2.salon_h1_scene import SalonH1Scene
from scenes_chapter_2.salon_h2_scene import SalonH2Scene
from scenes_chapter_2.salon_i1_scene import SalonI1
from scenes_chapter_2.salon_i2_scene import SalonI2
from scenes_chapter_2.banio_derecho_h_scene import BanioDerechoHScene
from scenes_chapter_2.banio_izquierdo_h_scene import BanioIzquierdoHScene
from scenes_chapter_2.banio_derecho_i_scene import BanioDerechoIScene
from scenes_chapter_2.banio_izquierdo_i_scene import BanioIzquierdoI
from scenes_chapter_2.conversacion_scena import show_conversation
from scenes_chapter_2.finCapitulo2 import FinCapitulo2Scene



from hud import HUD

# NUEVA FUNCIÓN PARA MOSTRAR LA PANTALLA NEGRA CON TEXTO
def show_black_screen_with_time(screen, clock, duration=3000):
    font = pygame.font.Font(None, 80)  # Puedes usar una fuente personalizada aquí si lo deseas
    text = font.render("4:50pm", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))  # Fondo negro
        screen.blit(text, text_rect)
        pygame.display.flip()
        clock.tick(60)

# FUNCIÓN PRINCIPAL DEL CAPÍTULO 2
def run_chapter2(screen):
    clock = pygame.time.Clock()

    # Mostrar pantalla negra con "4:50pm" durante 3 segundos
    show_black_screen_with_time(screen, clock, duration=3000)
    
    show_conversation(screen, clock)  # Duración total de la conversación (6 segundos)

    current_scene = EntradaNocheScene(screen)
    hud = HUD(current_scene.player)

    running = True
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        hud.handle_events(events)
        current_scene.handle_events(events)
        next_scene = current_scene.update(dt)

        if next_scene is not None:
            if next_scene == "sala":
                current_scene = SalaScene(screen, current_scene.player)
            elif next_scene == "cuarto":
                current_scene = FinCapitulo2Scene(screen, current_scene.player)  # Cambiar aquí por la nueva clase
            elif next_scene == "banio":
                current_scene = BanioScene(screen, current_scene.player)
            elif next_scene == "calle":
                current_scene = CalleScene(screen, current_scene.player)
            elif next_scene == "entrada_noche":
                current_scene = EntradaNocheScene(screen, current_scene.player)
            elif next_scene == "cafeteria_noche":
                current_scene = CafeteriaScene(screen, current_scene.player)
            elif next_scene == "jardineras_noche":
                current_scene = JardinerasNocheScene(screen, current_scene.player)
            elif next_scene == "interior_cafeteria":
                current_scene = InteriorCafeteriaScene(screen, current_scene.player)
            elif next_scene == "interior_edificio_h":
                current_scene = InteriorEdificioHScene(screen, current_scene.player)
            elif next_scene == "interior_edificio_h2":
                current_scene = InteriorEdificioH2Scene(screen, current_scene.player)
            elif next_scene == "salon_h1":
                current_scene = SalonH1Scene(screen, current_scene.player)
            elif next_scene == "salon_h2":
                current_scene = SalonH2Scene(screen, current_scene.player)
            elif next_scene == "banio_derecho_h":
                current_scene = BanioDerechoHScene(screen, current_scene.player)
            elif next_scene == "banio_izquierdo_h":
                current_scene = BanioIzquierdoHScene(screen, current_scene.player)
            elif next_scene == "interior_edificio_i":
                current_scene = InteriorEdificioI(screen, current_scene.player)
            elif next_scene == "interior_edificio_i2":
                current_scene = InteriorEdificioI2(screen, current_scene.player)
            elif next_scene == "salon_i1":
                current_scene = SalonI1(screen, current_scene.player)
            elif next_scene == "salon_i2":
                current_scene = SalonI2(screen, current_scene.player)
            elif next_scene == "banio_derecho_i":
                current_scene = BanioDerechoIScene(screen, current_scene.player)
            elif next_scene == "banio_izquierdo_i":
                current_scene = BanioIzquierdoI(screen, current_scene.player)
            elif next_scene == "restart":
                from main import main
                main()
                return

            hud.player = current_scene.player

        current_scene.render()
        hud.show_inventory = current_scene.get_hud_visibility()
        hud.render(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()