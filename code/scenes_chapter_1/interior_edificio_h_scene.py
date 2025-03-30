import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
import globales_chapter_1  # Variables globales del capítulo
from npc import NPC
from utils import draw_dialogue, draw_prompt
import globales_chapter_1
import conversaciones_chapter1  # Archivo con las líneas de conversación


class InteriorEdificioHScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("pasillo_h1.png")
        self.obstacles = get_collisions("hallway_h1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_edificio_h"
        # Creamos el NPC de Emiliano en (408, 272)
        self.emiliano_npc = NPC(408, 272, "emiliano_frente.png", "Emiliano", "")

        # Variables para gestionar la conversación
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
                            # Asignamos las líneas según la opción elegida
                            if self.conversation_selected_option == 0:
                                self.conversation_lines = (
                                    conversaciones_chapter1.CONVERSACION_EMILIAN_OPCION1
                                )
                            else:
                                self.conversation_lines = (
                                    conversaciones_chapter1.CONVERSACION_EMILIAN_OPCION2
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
                                # Marcar globalmente que la conversación ya se realizó
                                if (
                                    not globales_chapter_1.EMILIAN_CONVERSATION_DONE
                                    and self.conversation_options
                                ):
                                    globales_chapter_1.EMILIAN_CONVERSATION_DONE = True
                                self.conversation_mode = None
                                self.conversation_options = []
                                self.conversation_lines = []
                                self.conversation_line_index = 0

    def update(self, dt):
        if self.conversation_active:
            return None

        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Transición para regresar a jardineras
        door_interior_to_jardineras = pygame.Rect(285, 50, 115, 10)
        if self.player.rect.colliderect(door_interior_to_jardineras):
            self.player.rect.center = (866, 893)
            return "jardineras_noche"
        # Transición para ir a segundo piso
        door_interior_to_edificio_h2 = pygame.Rect(238, 494, 100, 10)
        if self.player.rect.colliderect(door_interior_to_edificio_h2):
            self.player.rect.center = (392, 411)
            return "interior_edificio_h2"
        # Transición para entrar al baño izquierdo
        door_interior_to_banio_izquierdo = pygame.Rect(198, 447, 5, 39)
        if self.player.rect.colliderect(door_interior_to_banio_izquierdo):
            self.player.rect.center = (468, 208)
            return "banio_izquierdo_h"
        # Transición para entrar al baño derecho
        door_interior_to_banio_derecho = pygame.Rect(457, 447, 5, 39)
        if self.player.rect.colliderect(door_interior_to_banio_derecho):
            self.player.rect.center = (81, 280)
            return "banio_derecho_h"

        # Interacción con el NPC
        if globales_chapter_1.EMILIAN_VISIBLE and self.player.rect.colliderect(
            self.emiliano_npc.rect
        ):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self.conversation_cooldown <= 0:
                if not globales_chapter_1.EMILIAN_CONVERSATION_DONE:
                    # Primera vez: iniciamos el modo elección
                    self.conversation_active = True
                    self.conversation_mode = "choice"
                    self.conversation_options = [
                        "Contarle a Emiliano sobre la sombra en el edificio i",
                        "No mencionarlo",
                    ]
                    self.conversation_selected_option = 0
                else:
                    # Conversación ya realizada: diálogo simple
                    self.conversation_active = True
                    self.conversation_mode = "branch"
                    self.conversation_lines = (
                        conversaciones_chapter1.CONVERSACION_EMILIAN_SIMPLE
                    )
                    self.conversation_line_index = 0
                self.conversation_cooldown = 500
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= dt

        return None

    def get_hud_visibility(self):
        # Si se está en conversación, ocultamos el HUD
        if self.conversation_active:
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
        if globales_chapter_1.EMILIAN_VISIBLE:
            self.emiliano_npc.draw(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Calcular escala para convertir coordenadas del mundo a pantalla
        scale_x = current_width / view_width
        scale_y = current_height / view_height

        # Mostrar prompt de interacción si el jugador está cerca del NPC y no hay conversación activa
        if (
            globales_chapter_1.EMILIAN_VISIBLE
            and not self.conversation_active
            and self.player.rect.colliderect(self.emiliano_npc.rect)
        ):
            npc_screen_x = (self.emiliano_npc.rect.centerx - camera_offset[0]) * scale_x
            npc_screen_y = (self.emiliano_npc.rect.top - camera_offset[1]) * scale_y
            prompt_pos = (npc_screen_x, npc_screen_y - 20)
            draw_prompt(self.screen, prompt_pos)

        # Mostrar diálogo si hay conversación activa
        if self.conversation_active:
            if self.conversation_mode == "choice":
                options_text = "\n".join(
                    [
                        "> " + opt if i == self.conversation_selected_option else opt
                        for i, opt in enumerate(self.conversation_options)
                    ]
                )
                draw_dialogue(self.screen, "Emiliano", options_text)
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
