import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from utils import draw_dialogue
import globales_chapter_1  # Módulo con las variables globales del capítulo


class JardinerasNocheScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        # Cargar los assets para jardineras_noche
        self.map = Map("window_espectro.png", "jardineras_noche.png")
        # Se asume que las colisiones están definidas con la clave "jardineras"
        self.obstacles = get_collisions("jardineras")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "jardineras_noche"

        # Variables para el evento de zoom
        self.zoom_event_triggered = False  # Para que se dispare solo una vez
        self.zoom_event_active = False  # Indica si se está mostrando el zoom
        self.zoom_event_timer = 0  # Duración del evento en ms

        # Variables para el diálogo al bloquear la transición
        self.dialogue = None
        self.dialogue_timer = 0

    def handle_events(self, events):
        pass

    def update(self, dt):
        # --- Evento de Zoom ---
        # Definimos el rectángulo que dispara el zoom (solo se activa una vez)
        zoom_trigger_rect = pygame.Rect(548, 460, 17, 515)
        if not self.zoom_event_triggered and self.player.rect.colliderect(
            zoom_trigger_rect
        ):
            self.zoom_event_triggered = True
            self.zoom_event_active = True
            self.zoom_event_timer = 3000  # El evento durará 3 segundos

        if self.zoom_event_active:
            self.zoom_event_timer -= dt
            if self.zoom_event_timer <= 0:
                self.zoom_event_active = False

        # Actualizar al jugador solo si no se está mostrando el evento de zoom
        if not self.zoom_event_active:
            self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # --- Actualización del diálogo ---
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.dialogue = None

        # --- Transiciones de Puertas ---
        # Transición a la cafetería
        door_jardineras_to_cafeteria = pygame.Rect(0, 0, 10, 1000)
        if self.player.rect.colliderect(door_jardineras_to_cafeteria):
            self.player.rect.center = (1460, 894)
            return "cafeteria_noche"

        # Transición a interior_edificio_h
        door_jardineras_to_edificio_h = pygame.Rect(772, 964, 193, 10)
        if self.player.rect.colliderect(door_jardineras_to_edificio_h):
            self.player.rect.center = (342, 118)
            return "interior_edificio_h"

        # Transición a interior_edificio_i
        door_jardineras_to_edificio_i = pygame.Rect(773, 317, 192, 4)
        if self.player.rect.colliderect(door_jardineras_to_edificio_i):
            if globales_chapter_1.INTERIOR_EDIFICIO_I_AVAILABLE:
                self.player.rect.center = (319, 453)
                return "interior_edificio_i"
            else:
                self.dialogue = "Primero debo ir a clase"
                self.dialogue_timer = 2000  # Mostrar mensaje durante 2 segundos

        return None

    def get_hud_visibility(self):
        # Si se está mostrando el zoom o hay algún diálogo, se oculta el inventario
        if self.zoom_event_active or self.dialogue:
            return False
        return True

    def render(self):
        if self.zoom_event_active:
            # Durante el evento de zoom, mostramos la sección definida y el texto
            zoom_rect = pygame.Rect(1202, 96, 211, 121)
            zoom_surface = self.map.fondo.subsurface(zoom_rect).copy()
            scaled_zoom = pygame.transform.scale(zoom_surface, self.screen.get_size())
            self.screen.blit(scaled_zoom, (0, 0))
            font = pygame.font.SysFont("arial", 36, bold=True)
            text_surface = font.render("¿Que es eso?", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(text_surface, text_rect)
            pygame.display.flip()
            return

        # Renderizado normal
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

        # Si hay un diálogo activo, se muestra usando la función draw_dialogue de utils.py
        if self.dialogue:
            draw_dialogue(self.screen, "", self.dialogue)
