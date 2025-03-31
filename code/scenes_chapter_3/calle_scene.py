import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_3.scene import Scene
from monster import Monster  # Asegúrate de importar la clase Monster

class CalleScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("camino_casa_noche.png", "camino_casa_noche_objetos.png")
        self.obstacles = get_collisions("calle")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "calle"

        # Crear 3 fantasmas en posiciones aleatorias
        self.ghosts = pygame.sprite.Group()
        for _ in range(3):
            x = random.randint(600, 1400)
            y = random.randint(300, 700)
            ghost_type = random.choice([1, 2, 3])
            ghost = Monster(x, y, ghost_type)
            ghost.speed = 60  # Más lento que el jugador
            self.ghosts.add(ghost)

        self.damage_timer = 0  # Tiempo de espera entre daños

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        for ghost in self.ghosts:
            ghost.update(self.player, dt)

        # Daño al jugador si lo toca un espectro
        if self.damage_timer > 0:
            self.damage_timer -= dt

        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect) and self.damage_timer <= 0:
                self.player.health -= 10
                self.damage_timer = 1000  # 1 segundo de invulnerabilidad

                if self.player.health <= 0:
                    from death import death_screen
                    death_screen(self.screen)

        # Transiciones
        if self.player.rect.colliderect(pygame.Rect(490, 250, 10, 250)):
            self.player.rect.center = (30, 385)
            return "sala"
        if self.player.rect.colliderect(pygame.Rect(0, 0, 500, 10)):
            self.player.rect.center = (50, 900)
            return "entrada_noche"
        return None

    def render(self):
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM

        camera_offset_x = self.player.rect.centerx - view_width / 2
        camera_offset_y = self.player.rect.centery - view_height / 2

        camera_offset_x = max(0, min(camera_offset_x, self.map.fondo_rect.width - view_width))
        camera_offset_y = max(0, min(camera_offset_y, self.map.fondo_rect.height - view_height))
        camera_offset = (camera_offset_x, camera_offset_y)

        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))

        self.map.draw_fondo(world_surface, camera_offset)

        for sprite in self.player_group:
            world_surface.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))

        # Dibujar fantasmas
        for ghost in self.ghosts:
            ghost.draw(world_surface, camera_offset)

        self.map.draw_primer_plano(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(world_surface, (current_width, current_height))
        self.screen.blit(scaled_surface, (0, 0))
