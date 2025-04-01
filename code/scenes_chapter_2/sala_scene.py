import pygame
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene
import globales_chapter_1  # Variables globales del capítulo
from npc import NPC
from utils import draw_dialogue, draw_prompt
import conversaciones_chapter1  # Archivo con las líneas de conversación para Gael


class SalaScene(Scene):
    def _init_(self, screen, player):
        super()._init_(screen)
        self.map = Map("casa_alex_sala.png")
        self.obstacles = get_collisions("casa_alex_sala")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("ambience.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "casa_alex_sala"
        self.closed_door_text = ""

        # --- Configuración del NPC de Gael ---
        # Se crea solo si GAEL_VISIBLE es True.
        if globales_chapter_1.GAEL_VISIBLE:
            self.gael_npc = NPC(829, 412, "gael_frente.png", "Gael", "")
        else:
            self.gael_npc = None

        # Variables para gestionar la conversación con Gael.
        # Si GAEL_CONVERSATION_DONE es False se permite la conversación con opciones.
        self.conversation_active = False  # Indica si hay conversación en curso
        self.conversation_mode = None  # "choice" o "branch"
        self.conversation_options = []  # Opciones de diálogo (modo "choice")
        self.conversation_selected_option = 0
        self.conversation_lines = []  # Líneas de diálogo para el modo "branch"
        self.conversation_line_index = 0  # Índice de la línea actual
        self.conversation_cooldown = 0  # Para evitar activaciones múltiples

    def handle_events(self, events):
        if self.conversation_active:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if self.conversation_mode == "choice":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.conversation_selected_option = (
                                self.conversation_selected_option - 1
                            ) % len(self.conversation_options)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.conversation_selected_option = (
                                self.conversation_selected_option + 1
                            ) % len(self.conversation_options)
                        elif event.key == pygame.K_e:
                            # Según la opción elegida, asignamos las líneas de conversación.
                            if self.conversation_selected_option == 0:
                                self.conversation_lines = (
                                    conversaciones_chapter1.CONVERSACION_GAEL_OPCION1
                                )
                            else:
                                self.conversation_lines = (
                                    conversaciones_chapter1.CONVERSACION_GAEL_OPCION2
                                )
                            self.conversation_mode = "branch"
                            self.conversation_line_index = 0
                    elif self.conversation_mode == "branch":
                        if event.key == pygame.K_e:
                            self.conversation_line_index += 1
                            if self.conversation_line_index >= len(
                                self.conversation_lines
                            ):
                                self.conversation_active = False
                                self.conversation_mode = None
                                self.conversation_options = []
                                self.conversation_lines = []
                                self.conversation_line_index = 0
                                # Marcar que la conversación con Gael ya se realizó
                                globales_chapter_1.GAEL_CONVERSATION_DONE = True
                                # Desbloquear la pantalla final
                                globales_chapter_1.FINAL_SCREEN_UNLOCKED = True

    def update(self, dt):
        # el jugador no se mueve si hay un dialogo activo
        if self.conversation_active:
            return None
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Transición: puerta para volver al cuarto (posición de la puerta: (895,165,10,40))
        door_sala_to_cuarto = pygame.Rect(895, 165, 10, 40)
        if self.player.rect.colliderect(door_sala_to_cuarto):
            self.player.rect.center = (30, 240)
            return "cuarto"
        # Transición: puerta para entrar al baño (posición: (805,80,40,10))
        door_sala_to_bathroom = pygame.Rect(805, 80, 40, 10)
        if self.player.rect.colliderect(door_sala_to_bathroom):
            self.player.rect.center = (145, 260)
            return "banio"
        # Transición: puerta para salir a la calle (posición: (0,395,10,70))
        door_sala_to_calle = pygame.Rect(0, 395, 10, 70)
        if self.player.rect.colliderect(door_sala_to_calle):
            self.player.rect.center = (470, 255)
            return "calle"

        # Puertas cerradas: mostrar diálogo "La puerta está cerrada" si se colisiona
        door_closed_hermano = pygame.Rect(895, 305, 10, 40)
        door_closed_papas = pygame.Rect(895, 475, 10, 40)
        if self.player.rect.colliderect(
            door_closed_hermano
        ) or self.player.rect.colliderect(door_closed_papas):
            self.closed_door_text = "La puerta está cerrada"
        else:
            self.closed_door_text = ""

        # --- Interacción con Gael ---
        # Solo se activa si Gael es visible y la conversación aún no se realizó
        if self.gael_npc and globales_chapter_1.GAEL_VISIBLE:
            if (
                not globales_chapter_1.GAEL_CONVERSATION_DONE
                and self.player.rect.colliderect(self.gael_npc.rect)
            ):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e] and self.conversation_cooldown <= 0:
                    self.conversation_active = True
                    self.conversation_mode = "choice"
                    self.conversation_options = [
                        "Mencionarle a Lucía",
                        "No mencionarle nada",
                    ]
                    self.conversation_selected_option = 0
                    self.conversation_cooldown = 500
            elif (
                globales_chapter_1.GAEL_CONVERSATION_DONE
                and self.player.rect.colliderect(self.gael_npc.rect)
            ):
                # Si la conversación ya se realizó, se muestra el diálogo simple
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e] and self.conversation_cooldown <= 0:
                    self.conversation_active = True
                    self.conversation_mode = "branch"
                    self.conversation_lines = (
                        conversaciones_chapter1.CONVERSACION_GAEL_SIMPLE
                    )
                    self.conversation_line_index = 0
                    self.conversation_cooldown = 500
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= dt

        return None

    def get_hud_visibility(self):
        # Ocultar el HUD mientras se está en conversación
        if self.conversation_active:
            return False

        if self.closed_door_text:
            return False

        return True

    def render(self):
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

        # Dibujar al NPC solo si la variable global lo permite
        if self.gael_npc and globales_chapter_1.GAEL_VISIBLE:
            world_surface.blit(
                self.gael_npc.image,
                (
                    self.gael_npc.rect.x - camera_offset[0],
                    self.gael_npc.rect.y - camera_offset[1],
                ),
            )

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Mostrar el diálogo de puertas cerradas si corresponde
        if self.closed_door_text:
            draw_dialogue(self.screen, "", self.closed_door_text)

        # Mostrar prompt de interacción para Gael
        if (
            self.gael_npc
            and globales_chapter_1.GAEL_VISIBLE
            and not self.conversation_active
            and self.player.rect.colliderect(self.gael_npc.rect)
        ):
            gael_screen_x = self.gael_npc.rect.centerx - camera_offset[0]
            gael_screen_y = self.gael_npc.rect.top - camera_offset[1]
            draw_prompt(self.screen, (gael_screen_x, gael_screen_y - 20))

        # Mostrar diálogo si hay conversación activa
        if self.conversation_active:

            if self.conversation_mode == "choice":
                options_text = "\n".join(
                    [
                        "> " + opt if i == self.conversation_selected_option else opt
                        for i, opt in enumerate(self.conversation_options)
                    ]
                )
                draw_dialogue(self.screen, "Gael", options_text)
            elif self.conversation_mode == "branch":
                if self.conversation_line_index < len(self.conversation_lines):
                    speaker, text = self.conversation_lines[
                        self.conversation_line_index
                    ]
                    draw_dialogue(self.screen, speaker, text)
                else:
                    self.conversation_active = False
                    self.conversation_mode = None
                    self.conversation_options = []
                    self.conversation_lines = []
                    self.conversation_line_index = 0