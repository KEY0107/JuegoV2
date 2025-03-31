import os
import pygame
import sys
import cv2
from settings import FPS  # Asegúrate de que FPS esté definido en settings

def start_screen(screen):
    """
    Pantalla de inicio que reproduce "pantallainicio_compatible.mp4" como fondo,
    muestra un menú con las opciones "Iniciar juego" y "Salir", y reproduce
    música de fondo.

    Se utiliza OpenCV para leer el video frame a frame, actualizándolo
    con un factor de lentitud.
    """
    # Subir un nivel desde "code" para llegar a la raíz del proyecto ("Terror")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construir las rutas de video y música
    video_path = os.path.join(base_path, "assets", "fondos", "pantallainicio_compatible.mp4")
    music_path = os.path.join(base_path, "assets", "sound", "song_bg.mp3")

    # Inicializar la captura de video con OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error al abrir el video en:", video_path)
        pygame.quit()
        sys.exit()

    # Cargar y reproducir música de fondo (en loop)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Inicializar joystick si está conectado
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    # Definir las opciones del menú y la opción seleccionada inicialmente
    options = ["Iniciar juego", "Salir"]
    selected_option = 0

    font = pygame.font.SysFont("arial", 36)
    clock = pygame.time.Clock()

    # Obtener el fps del video; si falla, se usa 60 por defecto
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 60

    # Factor para ralentizar el video (1 = velocidad normal)
    slow_factor = 1
    effective_fps = video_fps * slow_factor
    frame_interval = 1000 / effective_fps  # en milisegundos

    last_frame_time = pygame.time.get_ticks()
    last_frame_surface = None

    # Variables para manejar el movimiento del joystick (ejes)
    joystick_deadzone = 0.5
    axis_moved = False  # para evitar cambios múltiples

    while True:
        # Obtener el tamaño actual de la ventana
        current_width, current_height = screen.get_size()

        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time >= frame_interval:
            ret, frame = cap.read()
            if not ret:
                # Reinicia el video si llega al final
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            # Convertir el frame de BGR a RGB y a superficie de pygame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            last_frame_surface = pygame.image.frombuffer(
                frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB"
            )
            # Escalar el frame a las dimensiones actuales de la ventana
            last_frame_surface = pygame.transform.scale(
                last_frame_surface, (current_width, current_height)
            )
            last_frame_time = current_time

        if last_frame_surface:
            screen.blit(last_frame_surface, (0, 0))

        # Dibujar las opciones del menú sobre el video, usando el tamaño actual de la ventana
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (255, 255, 255)
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect(
                center=(current_width // 2, current_height - 100 + i * 40)
            )
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_option = (selected_option - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_e:
                    if options[selected_option] == "Iniciar juego":
                        cap.release()
                        pygame.mixer.music.fadeout(1000)
                        return  # Iniciar el juego
                    elif options[selected_option] == "Salir":
                        cap.release()
                        pygame.mixer.music.fadeout(1000)
                        pygame.quit()
                        sys.exit()

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if options[selected_option] == "Iniciar juego":
                        cap.release()
                        pygame.mixer.music.fadeout(1000)
                        return  # Iniciar el juego
                    elif options[selected_option] == "Salir":
                        cap.release()
                        pygame.mixer.music.fadeout(1000)
                        pygame.quit()
                        sys.exit()

            if event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:
                    selected_option = (selected_option - 1) % len(options)
                elif event.value[1] == -1:
                    selected_option = (selected_option + 1) % len(options)

            if event.type == pygame.JOYAXISMOTION and event.axis == 0:
                if not axis_moved:
                    if event.value < -joystick_deadzone:
                        selected_option = (selected_option - 1) % len(options)
                        axis_moved = True
                    elif event.value > joystick_deadzone:
                        selected_option = (selected_option + 1) % len(options)
                        axis_moved = True
                if abs(event.value) < 0.2:
                    axis_moved = False
