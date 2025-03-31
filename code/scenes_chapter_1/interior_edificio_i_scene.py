import pygame
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene
from utils import draw_dialogue
import globales_chapter_1  # Variables globales del capítulo


class InteriorEdificioI(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("pasillo_i1.png")
        self.obstacles = get_collisions("hallway_i1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("hallway.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_edificio_i"

        # Agregar la nota
        try:
            self.note_img = pygame.image.load(
                "../assets/items/nota1.png"
            ).convert_alpha()
            self.note_img = pygame.transform.scale(self.note_img, (20, 20))
        except Exception as e:
            print("Error cargando nota:", e)
            self.note_img = None
        # Posición de la nota en el mapa (ajusta según convenga)
        self.note_rect = (
            self.note_img.get_rect(topleft=(142, 248))
            if self.note_img
            else pygame.Rect(142, 248, 20, 20)
        )
        self.note_collected = False

        # Variables para el diálogo de la nota
        self.note_dialogue_active = False
        self.note_dialogue_lines = []  # Lista de tuplas (speaker, texto)
        self.note_dialogue_index = 0

        # Si ya se vio la nota en una entrada anterior, deshabilitamos su interacción
        if globales_chapter_1.NOTA_ALREADY_SEEN:
            self.note_unavailable = True
        else:
            self.note_unavailable = False

    def handle_events(self, events):
        # Procesa la pulsación de E para avanzar en el diálogo de la nota
        for event in events:
            if self.note_dialogue_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.note_dialogue_index += 1
                    if self.note_dialogue_index >= len(self.note_dialogue_lines):
                        self.note_dialogue_active = False
                        globales_chapter_1.NOTA_DIALOGO = True

    def update(self, dt):

        if self.note_dialogue_active:
            return None

        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Transición para regresar a jardineras
        door_interior_to_jardineras = pygame.Rect(221, 496, 200, 5)
        if self.player.rect.colliderect(door_interior_to_jardineras):
            globales_chapter_1.NOTA_ALREADY_SEEN = (
                True  # Marca que ya se mostró la nota
            )
            self.player.rect.center = (871, 392)
            return "jardineras_noche"

        # Transición para ir a segundo piso
        door_interior_to_edificio_h2 = pygame.Rect(303, 22, 93, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_h2):
            globales_chapter_1.NOTA_ALREADY_SEEN = True
            self.player.rect.center = (336, 429)
            return "interior_edificio_i2"

        # Transición para entrar al baño izquierdo
        door_interior_to_banio_izquierdo = pygame.Rect(197, 109, 5, 47)
        if self.player.rect.colliderect(door_interior_to_banio_izquierdo):
            globales_chapter_1.NOTA_ALREADY_SEEN = True
            self.player.rect.center = (485, 265)
            return "banio_izquierdo_i"

        # Transición para entrar al baño derecho
        door_interior_to_banio_derecho = pygame.Rect(454, 109, 5, 47)
        if self.player.rect.colliderect(door_interior_to_banio_derecho):
            globales_chapter_1.NOTA_ALREADY_SEEN = True
            self.player.rect.center = (68, 280)
            return "banio_derecho_i"

        # Si la nota está desbloqueada, no fue recogida, y aún está disponible (única vez)
        if (
            globales_chapter_1.NOTA_UNLOCKED
            and not self.note_collected
            and not self.note_unavailable
        ):
            if self.player.rect.colliderect(self.note_rect):
                self.note_collected = True
                # Iniciar diálogo de la nota (si no se mostró antes)
                if not globales_chapter_1.NOTA_DIALOGO:
                    self.note_dialogue_active = True
                    self.note_dialogue_index = 0
                    self.note_dialogue_lines = [
                        (
                            "Nota",
                            "¿Quién lo decidirá al final? A veces me pregunto si todo esto tuvo sentido.",
                        ),
                        ("Alex", "¿Alguien la olvidó?"),
                    ]
        return None

    def get_hud_visibility(self):
        # ocultar el hud cuando este la conversacion de la nota o de alex
        if self.note_dialogue_active:
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

        # Dibujar la nota en el mundo si aún no se recogió
        if (
            globales_chapter_1.NOTA_UNLOCKED
            and not self.note_collected
            and not globales_chapter_1.NOTA_ALREADY_SEEN
            and self.note_img
        ):
            note_screen_pos = (
                self.note_rect.x - camera_offset[0],
                self.note_rect.y - camera_offset[1],
            )
            world_surface.blit(self.note_img, note_screen_pos)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Si el diálogo de la nota está activo, mostrar la línea actual
        if self.note_dialogue_active:
            speaker, text = self.note_dialogue_lines[self.note_dialogue_index]
            draw_dialogue(self.screen, speaker, text, "Alex_confundido_conversation")
