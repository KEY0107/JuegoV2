import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path="../assets/characters/NPC_1.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))


class Fantasma(pygame.sprite.Sprite):
    def __init__(self, positions, image_path="../assets/characters/fantasma_frente.png"):
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


class EntradaNocheScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("entrada_noche.png", "entrada_noche_obstaculos.png")
        self.obstacles = get_collisions("entrada")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "entrada_noche"

        # NPCs
        self.npc1 = NPC(159, 789, "../assets/characters/NPC_1.png")
        self.npc2 = NPC(1215, 461, "../assets/characters/NPC_2.png")
        self.npc_group = pygame.sprite.Group(self.npc1, self.npc2)

        # Agregar colisiones
        self.obstacles.append(self.npc1.rect)
        self.obstacles.append(self.npc2.rect)

        # Fantasma
        self.fantasma_positions = [
            (400, 700),
            (800, 800),
            (600, 500),
            (1000, 650),
            (300, 600),
            (1200, 450)
        ]
        self.fantasma = Fantasma(self.fantasma_positions)

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Actualizar el fantasma
        current_time = pygame.time.get_ticks()
        self.fantasma.update(current_time)

        # Transiciones
        door_entrada_to_calle = pygame.Rect(0, 960, 300, 10)
        if self.player.rect.colliderect(door_entrada_to_calle):
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

        # Dibujar NPCs
        for npc in self.npc_group:
            world_surface.blit(
                npc.image,
                (npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1])
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
