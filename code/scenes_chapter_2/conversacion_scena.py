import pygame
import sys

def show_conversation(screen, clock):
    # Definir la conversación
    conversation_lines = [
        ("Emiliano", "La maestra cancelo las 2 horas de clase, para que no vayas tan temprano"),
        ("Alex", "Nmms, neta? ya estoy en la uni"),
        ("Emiliano", "jajaja, lo siento, apenas aviso")
    ]

    # Configuración de la fuente
    font = pygame.font.SysFont("arial", 24)
    conversation_index = 0
    conversation_timer = 2000  # 2 segundos por mensaje
    conversation_active = True  # Activar la conversación
    start_time = pygame.time.get_ticks()

    # Reproducir el sonido de charla
    pygame.mixer.init()  # Inicializa el mezclador de audio
    charla_sound = pygame.mixer.Sound("assets/sound/charla.mp3")
    charla_sound.play(-1)  # Reproduce el sonido en bucle mientras se muestra la conversación

    while conversation_index < len(conversation_lines):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Mostrar la pantalla negra
        screen.fill((0, 0, 0))  # Fondo negro

        if conversation_active:
            # Mostrar el siguiente mensaje si la conversación está activa
            speaker, text = conversation_lines[conversation_index]
            rendered_text = font.render(f"{speaker}: {text}", True, (255, 255, 255))
            text_x = (screen.get_width() - rendered_text.get_width()) // 2
            text_y = (screen.get_height() - rendered_text.get_height()) // 2
            screen.blit(rendered_text, (text_x, text_y))

            # Temporizador para avanzar al siguiente mensaje
            if pygame.time.get_ticks() - start_time >= conversation_timer:
                conversation_index += 1
                start_time = pygame.time.get_ticks()  # Reiniciar el temporizador para el siguiente mensaje

        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(60)

    charla_sound.stop()  # Detener el sonido una vez que la conversación haya terminado
    return