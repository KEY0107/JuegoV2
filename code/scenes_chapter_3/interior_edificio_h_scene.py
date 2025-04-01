import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
import globales_chapter_1


class Fantasma(pygame.sprite.Sprite):
    def __init__(self, positions, image_path="assets/characters/fantasma_frente.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.positions = positions
        self.current_position = random.choice(self.positions)
        self.rect = self.image.get_rect(topleft=self.current_position)
        self.visible = True
        self.timer = pygame.time.get_ticks()
        self.interval = 3000  # 3 segundos

    def update(self, current_time):
        if current_time - self.timer >= self.interval:
            self.timer = current_time
            self.visible = not self.visible
            if self.visible:
                self.current_position = random.choice(self.positions)
                self.rect.topleft = self.current_position


class InteriorEdificioHScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("pasillo_h1.png")
        self.obstacles = get_collisions("hallway_h1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_edificio_h"

        # Fantasma
        self.fantasma_positions = [
            (118, 365),
            (271, 217),
            (498, 350),
            (376, 476)
        ]
        self.fantasma = Fantasma(self.fantasma_positions)

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Actualizar fantasma
        current_time = pygame.time.get_ticks()
        self.fantasma.update(current_time)

        # Transición a jardineras
        if self.player.rect.colliderect(pygame.Rect(285, 50, 115, 10)):
            self.player.rect.center = (866, 893)
            return "jardineras_noche"

        # Transición a segundo piso
        if self.player.rect.colliderect(pygame.Rect(238, 494, 100, 10)):
            self.player.rect.center = (392, 411)
            return "interior_edificio_h2"

        # Baño izquierdo
        if self.player.rect.colliderect(pygame.Rect(198, 447, 5, 39)):
            self.player.rect.center = (468, 208)
            return "banio_izquierdo_h"

        # Baño derecho
        if self.player.rect.colliderect(pygame.Rect(457, 447, 5, 39)):
            self.player.rect.center = (81, 280)
            return "banio_derecho_h"

        return None

    def get_hud_visibility(self):
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
            camera_offset_x = max(0, min(camera_offset_x, self.map.fondo_rect.width - view_width))

        if self.map.fondo_rect.height < view_height:
            camera_offset_y = (self.map.fondo_rect.height - view_height) / 2
        else:
            camera_offset_y = max(0, min(camera_offset_y, self.map.fondo_rect.height - view_height))

        camera_offset = (camera_offset_x, camera_offset_y)

        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))

        self.map.draw_fondo(world_surface, camera_offset)

        # Dibujar jugador
        for sprite in self.player_group:
            world_surface.blit(
                sprite.image,
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1])
            )

        # Dibujar fantasma si está visible
        if self.fantasma.visible:
            world_surface.blit(
                self.fantasma.image,
                (self.fantasma.rect.x - camera_offset[0], self.fantasma.rect.y - camera_offset[1])
            )

        self.map.draw_primer_plano(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(world_surface, (current_width, current_height))
        self.screen.blit(scaled_surface, (0, 0))
