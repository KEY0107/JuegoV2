import pygame
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene


class SalaScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("casa_alex_sala.png")
        self.obstacles = get_collisions("casa_alex_sala")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("ciudad.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "casa_alex_sala"
        self.closed_door_text = ""

    def handle_events(self, events):
        pass

    def get_hud_visibility(self):
        return self.closed_door_text == ""

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)
        # Transición: si colisiona con la puerta para volver al cuarto, definida en (895,165,10,40)
        door_sala_to_cuarto = pygame.Rect(895, 165, 10, 40)
        if self.player.rect.colliderect(door_sala_to_cuarto):
            # Posicionar al jugador en la entrada de la puerta del cuarto
            self.player.rect.center = (30, 240)  # Ajusta este valor según tu asset
            return "cuarto"
        # Transición: si colisiona con la puerta para entrar al baño, definida en (805,80,40,10)
        door_sala_to_bathroom = pygame.Rect(805, 80, 40, 10)
        if self.player.rect.colliderect(door_sala_to_bathroom):
            self.player.rect.center = (145, 260)
            return "banio"
        door_sala_to_calle = pygame.Rect(0, 395, 10, 70)
        if self.player.rect.colliderect(door_sala_to_calle):
            # Posicionar al jugador en la entrada de la calle; por ejemplo, (470,255)
            self.player.rect.center = (470, 255)
            return "calle"

        # Si no se produce ninguna transición, se evalúa la colisión con puertas cerradas.
        door_closed_hermano = pygame.Rect(895, 305, 10, 40)
        door_closed_papas = pygame.Rect(895, 475, 10, 40)
        if self.player.rect.colliderect(
            door_closed_hermano
        ) or self.player.rect.colliderect(door_closed_papas):
            self.closed_door_text = "La puerta está cerrada"
        else:
            self.closed_door_text = ""
        return None

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
        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))
        # Si se detecta colisión con puertas cerradas, mostrar el diálogo "La puerta está cerrada"
        if self.closed_door_text:
            from utils import draw_dialogue

            draw_dialogue(self.screen, "", self.closed_door_text)
