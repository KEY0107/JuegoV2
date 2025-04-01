import pygame
import sys
import pygame.time
import cv2
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from utils import draw_dialogue
from scenes_chapter_3.salon_h1_scene import SalonH1Scene  # Importar para acceder a note_taken_flag


class BanioIzquierdoHScene(Scene):
    cinematica_mostrada = False

    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("bathroom_HL.png")
        self.obstacles = get_collisions("banio_izquierdo_h")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "banio_izquierdo_h"

        self.cinematic_done = BanioIzquierdoHScene.cinematica_mostrada
        self.black_screen_timer = 1000  # 1 segundo
        self.post_cinematic_dialogue = False
        self.dialogue_closed = False

        if SalonH1Scene.note_taken_flag and not self.cinematic_done:
            self.play_cinematic(screen)
            BanioIzquierdoHScene.cinematica_mostrada = True
            self.cinematic_done = True
            self.start_time = pygame.time.get_ticks()
            self.show_black_screen = True
        else:
            self.show_black_screen = False

    def play_cinematic(self, screen, video_path="assets/fondos/cinematicaBanoCap3.mp4"):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error al abrir el video.")
            return

        clock = pygame.time.Clock()
        fps = cap.get(cv2.CAP_PROP_FPS)

        font = pygame.font.SysFont("arial", 28, bold=True)
        full_dialogue = "Lucía: ¿Por qué? ¿Por qué lo hiciste? Confiaba en ti... ¿Por qué me hiciste esto?"

        while cap.isOpened():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame)
            frame_surface = pygame.surfarray.make_surface(frame)
            frame_surface = pygame.transform.scale(frame_surface, screen.get_size())

            screen.blit(frame_surface, (0, 0))

            # Mostrar diálogo completo
            text_surface = font.render(full_dialogue, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            screen.blit(text_surface, text_rect)

            pygame.display.flip()
            clock.tick(fps * 0.25)  # Ralentiza el video 4x para extender la duración

        cap.release()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.post_cinematic_dialogue:
                    self.dialogue_closed = True

    def update(self, dt):
        if self.show_black_screen:
            if pygame.time.get_ticks() - self.start_time >= self.black_screen_timer:
                self.show_black_screen = False
                self.post_cinematic_dialogue = True
            return None

        if not self.show_black_screen and (not self.post_cinematic_dialogue or self.dialogue_closed):
            self.player.update(dt, self.obstacles)
            self.player.clamp_within_map(self.map.fondo_rect)

        door_interior_to_edificio_h = pygame.Rect(547, 232, 5, 93)
        if self.player.rect.colliderect(door_interior_to_edificio_h):
            self.player.rect.center = (234, 437)
            return "interior_edificio_h"

        return None


    def get_hud_visibility(self):
        return not self.post_cinematic_dialogue or self.dialogue_closed

    def render(self):
        if self.show_black_screen:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            return

        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM
        camera_offset_x = self.player.rect.centerx - view_width / 2
        camera_offset_y = self.player.rect.centery - view_height / 2

        if self.map.fondo_rect.width < view_width:
            camera_offset_x = (self.map.fondo_rect.width - view_width) / 2
        else:
            camera_offset_x = max(0, min(camera_offset_x, self.map.fondo_rect.width - view_width))

        if self.map.fondo_rect.height < view_height:
            camera_offset_y = (self.map.fondo_rect.height - view_height) / 2
        else:
            camera_offset_y = max(0, min(camera_offset_y, self.map.fondo_rect.height - view_height))

        camera_offset = (camera_offset_x, camera_offset_y)
        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))

        self.map.draw_fondo(world_surface, camera_offset)

        for sprite in self.player_group:
            world_surface.blit(
                sprite.image,
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1])
            )

        self.map.draw_primer_plano(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(world_surface, (current_width, current_height))
        self.screen.blit(scaled_surface, (0, 0))

        if self.post_cinematic_dialogue and not self.dialogue_closed:
            draw_dialogue(self.screen, "Alex", "¿Qué fue eso...? Mejor iré a casa.")