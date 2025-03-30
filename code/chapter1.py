import pygame
import sys
from scenes_chapter_1.cuarto_scene import CuartoScene
from scenes_chapter_1.sala_scene import SalaScene
from scenes_chapter_1.banio_scene import BanioScene
from scenes_chapter_1.calle_scene import CalleScene
from scenes_chapter_1.entrada_noche_scene import EntradaNocheScene
from scenes_chapter_1.cafeteria_scene import CafeteriaScene
from scenes_chapter_1.jardineras_noche import JardinerasNocheScene
from scenes_chapter_1.interior_cafeteria import InteriorCafeteriaScene
from scenes_chapter_1.interior_edificio_h_scene import InteriorEdificioHScene
from scenes_chapter_1.interior_edificio_h2_scene import InteriorEdificioH2Scene
from scenes_chapter_1.interior_edificio_i_scene import InteriorEdificioI
from scenes_chapter_1.interior_edificio_i2_scene import InteriorEdificioI2
from scenes_chapter_1.salon_h1_scene import SalonH1Scene
from scenes_chapter_1.salon_h2_scene import SalonH2Scene
from scenes_chapter_1.salon_i1_scene import SalonI1
from scenes_chapter_1.salon_i2_scene import SalonI2
from scenes_chapter_1.banio_derecho_h_scene import BanioDerechoHScene
from scenes_chapter_1.banio_izquierdo_h_scene import BanioIzquierdoHScene
from scenes_chapter_1.banio_derecho_i_scene import BanioDerechoIScene
from scenes_chapter_1.banio_izquierdo_i_scene import BanioIzquierdoI
from hud import HUD


def run_chapter1(screen):
    clock = pygame.time.Clock()
    current_scene = CuartoScene(screen, show_initial_dialogue=True)
    hud = HUD(current_scene.player)  # Inicializa el HUD con el jugador actual

    running = True
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        current_scene.handle_events(events)
        next_scene = current_scene.update(dt)
        if next_scene is not None:
            if next_scene == "sala":
                current_scene = SalaScene(screen, current_scene.player)
                hud.player = current_scene.player
            elif next_scene == "cuarto":
                # Al regresar al cuarto, se pasa el objeto jugador actual para conservar la posición
                current_scene = CuartoScene(
                    screen, show_initial_dialogue=False, player=current_scene.player
                )
                hud.player = current_scene.player
            elif next_scene == "banio":
                current_scene = BanioScene(screen, current_scene.player)
                hud.player = current_scene.player
            elif next_scene == "calle":
                current_scene = CalleScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "entrada_noche":
                current_scene = EntradaNocheScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "cafeteria_noche":
                current_scene = CafeteriaScene(screen, current_scene.player)
                hud.player = current_scene.player
            elif next_scene == "jardineras_noche":
                current_scene = JardinerasNocheScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "interior_cafeteria":
                current_scene = InteriorCafeteriaScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "interior_edificio_h":
                current_scene = InteriorEdificioHScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "interior_edificio_h2":
                current_scene = InteriorEdificioH2Scene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "salon_h1":
                current_scene = SalonH1Scene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "salon_h2":
                current_scene = SalonH2Scene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "banio_derecho_h":
                current_scene = BanioDerechoHScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "banio_izquierdo_h":
                current_scene = BanioIzquierdoHScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "interior_edificio_i":
                current_scene = InteriorEdificioI(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "interior_edificio_i2":
                current_scene = InteriorEdificioI2(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "salon_i1":
                current_scene = SalonI1(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "salon_i2":
                current_scene = SalonI2(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "banio_derecho_i":
                current_scene = BanioDerechoIScene(screen, current_scene.player)
                hud.player = current_scene.player

            elif next_scene == "banio_izquierdo_i":
                current_scene = BanioIzquierdoI(screen, current_scene.player)
                hud.player = current_scene.player

        current_scene.render()
        hud.render(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
