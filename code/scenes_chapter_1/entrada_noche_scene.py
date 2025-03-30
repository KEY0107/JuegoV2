import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene


class EntradaNocheScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        # Suponemos que los assets para entrada_noche están en "entrada_noche.png" y "entrada_noche_objetos.png"
        self.map = Map("entrada_noche.png", "entrada_noche_obstaculos.png")
        self.obstacles = get_collisions("entrada")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "entrada_noche"

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)
        # Ejemplo de transición: si el jugador colisiona con la zona de salida hacia la calle
        door_entrada_to_calle = pygame.Rect(0, 960, 300, 10)
        if self.player.rect.colliderect(door_entrada_to_calle):
            # Reposicionar al jugador en la entrada de la calle; ajusta según convenga
            self.player.rect.center = (350, 60)
            return "calle"
        door_entrada_to_cafeteria = pygame.Rect(1490, 0, 10, 1000)
        if self.player.rect.colliderect(door_entrada_to_cafeteria):
            self.player.rect.center = (150, 860)
            return "cafeteria_noche"
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
