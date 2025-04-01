import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from monster import Monster
from death import death_screen


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path="/assets/characters/NPC_1.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))


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
        self.npc1 = NPC(159, 789, "/assets/characters/NPC_1.png")
        self.npc2 = NPC(1215, 461, "/assets/characters/NPC_2.png")
        self.npc_group = pygame.sprite.Group(self.npc1, self.npc2)

        # Agregar colisiones
        self.obstacles.append(self.npc1.rect)
        self.obstacles.append(self.npc2.rect)

        # MONSTRUOS
        self.monsters = pygame.sprite.Group()
        self.spawn_monsters(5)

        self.damage_cooldown = 1000  # 1 segundo entre daños
        self.last_damage_time = 0

    def spawn_monsters(self, count):
        for _ in range(count):
            x = random.randint(300, 1200)
            y = random.randint(400, 800)
            ghost_type = random.choice([1, 2, 3])
            monster = Monster(x, y, ghost_type)
            monster.speed = 60  # Más lento
            self.monsters.add(monster)

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        current_time = pygame.time.get_ticks()
        for monster in self.monsters:
            monster.update(self.player, dt)
            if self.player.rect.colliderect(monster.rect):
                if current_time - self.last_damage_time > self.damage_cooldown:
                    self.player.health -= 10
                    self.last_damage_time = current_time
                    if self.player.health <= 0:
                        if death_screen(self.screen):
                            return "restart"

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

        for sprite in self.player_group:
            world_surface.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))

        for npc in self.npc_group:
            world_surface.blit(npc.image, (npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1]))

        for monster in self.monsters:
            monster.draw(world_surface, camera_offset)

        self.map.draw_primer_plano(world_surface, camera_offset)

        scaled_surface = pygame.transform.scale(world_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
