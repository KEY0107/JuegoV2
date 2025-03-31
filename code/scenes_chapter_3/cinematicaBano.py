import cv2
import pygame
import sys

class Cinematica:
    @staticmethod
    def play(screen, video_path="/assets/fondos/cinematicaBanoCap3.mp4"):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error al abrir el video.")
            return

        clock = pygame.time.Clock()
        fps = cap.get(cv2.CAP_PROP_FPS)

        while cap.isOpened():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()

            ret, frame = cap.read()
            if not ret:
                break  # Se terminó el video

            # Convertir frame de BGR (OpenCV) a RGB (Pygame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame)  # Opcional: para ajustar orientación si es necesario
            frame_surface = pygame.surfarray.make_surface(frame)

            # Escalar al tamaño de la pantalla
            frame_surface = pygame.transform.scale(frame_surface, screen.get_size())

            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            clock.tick(fps)

        cap.release()
