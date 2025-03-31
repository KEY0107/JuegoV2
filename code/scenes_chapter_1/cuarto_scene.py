import pygame
from map import Map
from collision_data import get_collisions
from player import Player
from sound_manager import SoundManager
from utils import draw_dialogue
from scenes_chapter_1.scene import Scene
import globales_chapter_1  # Módulo con las variables globales del capítulo


class CuartoScene(Scene):
    def __init__(self, screen, show_initial_dialogue=True, player=None):
        super().__init__(screen)
        self.map = Map("casa_alex_cuarto.png")
        self.obstacles = get_collisions("casa_alex_cuarto")
        # Si se pasa un jugador, se conserva su posición
        if player is None:
            self.player = Player(180, 170)
        else:
            self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("ambience.mp3", fade_in_ms=1000)
        self.DEFAULT_ZOOM = 2
        self.current_map = "casa_alex_cuarto"
        self.initial_dialogue_active = show_initial_dialogue
        self.initial_dialogue_text = "Se me hace tarde para ir a la universidad"

        # // NUEVO: Variables para la secuencia final
        self.final_screen_phase = (
            None  # None si aún no se ha iniciado la secuencia final
        )
        self.final_screen_timer = 0
        self.final_screen_image = None  # Se cargará la imagen del teléfono

    def get_hud_visibility(self):
        # Mientras se muestre la conversación o la secuencia final no se muestra el HUD
        if self.initial_dialogue_active or self.final_screen_phase is not None:
            return False
        return True

    def handle_events(self, events):
        # Si se está en la secuencia final, no se procesan eventos
        if self.final_screen_phase is not None:
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.initial_dialogue_active and event.key == pygame.K_e:
                    self.initial_dialogue_active = False

    def update(self, dt):
        # // NUEVO: Si la variable global FINAL_SCREEN_UNLOCKED es True, iniciar/actualizar secuencia final
        if globales_chapter_1.FINAL_SCREEN_UNLOCKED:
            if self.final_screen_phase is None:
                # Inicia la secuencia final en la fase 0 (mostrar imagen y mensaje)
                self.final_screen_phase = 0
                self.final_screen_timer = 3000  # 3 segundos
                # Cargar la imagen (ajusta la ruta si es necesario)
                self.final_screen_image = pygame.image.load(
                    "../assets/items/unknown_mensaje.png"
                ).convert_alpha()
            else:
                self.final_screen_timer -= dt
                # Cuando termine la fase 0, pasa a la fase 1
                if self.final_screen_phase == 0 and self.final_screen_timer <= 0:
                    self.final_screen_phase = 1
                    self.final_screen_timer = (
                        3000  # 3 segundos para la pantalla de "FIN DEL CAPITULO"
                    )
            # Durante la secuencia final no se actualiza al jugador
            return None

        # Actualización normal si no se muestra la secuencia final
        if not self.initial_dialogue_active:
            self.player.update(dt, self.obstacles)
            self.player.clamp_within_map(self.map.fondo_rect)
        # Transición automática: si colisiona con la puerta para salir del cuarto, definida en (0,235,10,40)
        door_cuarto_to_sala = pygame.Rect(0, 235, 10, 40)
        if self.player.rect.colliderect(door_cuarto_to_sala):
            # Al salir del cuarto, se quiere que el jugador aparezca en la sala en (880,165)
            self.player.rect.center = (880, 165)
            return "sala"
        return None

    def render(self):
        # // NUEVO: Si se está en la secuencia final, se renderiza la pantalla final y se sale
        if self.final_screen_phase is not None:
            if self.final_screen_phase == 0:
                # Fase 0: mostrar pantalla negra con la imagen del teléfono y el mensaje
                self.screen.fill((0, 0, 0))
                if self.final_screen_image:
                    # Centramos la imagen en pantalla
                    image_rect = self.final_screen_image.get_rect(
                        center=(
                            self.screen.get_width() // 2,
                            self.screen.get_height() // 2,
                        )
                    )
                    self.screen.blit(self.final_screen_image, image_rect)
                font = pygame.font.SysFont("arial", 36, bold=False)
                text_surface = font.render(
                    "No lo ignores. Pregunta a los que estuvieron ahí.",
                    True,
                    (255, 255, 255),
                )
                text_rect = text_surface.get_rect(
                    center=(
                        self.screen.get_width() // 2,
                        self.screen.get_height() // 2 + 100,
                    )
                )
                self.screen.blit(text_surface, text_rect)
                pygame.display.flip()
                return
            elif self.final_screen_phase == 1:
                # Fase 1: mostrar pantalla negra con el texto "FIN DEL CAPITULO"
                self.screen.fill((0, 0, 0))
                font = pygame.font.SysFont("arial", 48, bold=True)
                text_surface = font.render("FIN DEL CAPITULO", True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
                )
                self.screen.blit(text_surface, text_rect)
                pygame.display.flip()
                return

        # Renderizado normal de la escena
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM
        camera_offset_x = self.player.rect.centerx - view_width / 2
        camera_offset_y = self.player.rect.centery - view_height / 2
        if self.map.fondo_rect.width < view_width:
            camera_offset_x = (self.map.fondo_rect.width - view_width) / 2
        else:
            camera_offset_x = max(
                0, min(camera_offset_x, self.map.fondo_rect.width - view_width)
            )
        if self.map.fondo_rect.height < view_height:
            camera_offset_y = (self.map.fondo_rect.height - view_height) / 2
        else:
            camera_offset_y = max(
                0, min(camera_offset_y, self.map.fondo_rect.height - view_height)
            )
        camera_offset = (camera_offset_x, camera_offset_y)
        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))
        self.map.draw_fondo(world_surface, camera_offset)
        for sprite in self.player_group:
            world_surface.blit(
                sprite.image,
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]),
            )
        self.map.draw_primer_plano(world_surface, camera_offset)
        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))
        if self.initial_dialogue_active:
            draw_dialogue(
                self.screen,
                "Alex",
                self.initial_dialogue_text,
                "Alex_normal_conversation",
            )
