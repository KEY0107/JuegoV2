import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from utils import draw_dialogue
import globales_chapter_1

from monster import Monster
from death import death_screen  # Importar la pantalla de muerte


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path="assets/characters/NPC_1.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))


class Fantasma(pygame.sprite.Sprite):
    def __init__(self, positions, image_path="assets/characters/fantasma_frente.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.positions = positions
        self.current_position = random.choice(self.positions)
        self.rect = self.image.get_rect(topleft=self.current_position)
        self.visible = True
        self.timer = pygame.time.get_ticks()
        self.interval = 3000

    def update(self, current_time):
        if current_time - self.timer >= self.interval:
            self.timer = current_time
            self.visible = not self.visible
            if self.visible:
                self.current_position = random.choice(self.positions)
                self.rect.topleft = self.current_position


class JardinerasNocheScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("window_espectro.png", "jardineras_noche.png")
        self.obstacles = get_collisions("jardineras")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "jardineras_noche"

        # NPCs
        self.npc1 = NPC(375, 840, "assets/characters/NPC_4.png")
        self.npc2 = NPC(1010, 530, "assets/characters/NPC_5.png")
        self.npc3 = NPC(1260, 845, "assets/characters/NPC_3.png")
        self.npc_group = pygame.sprite.Group(self.npc1, self.npc2, self.npc3)
        self.obstacles.extend([self.npc1.rect, self.npc2.rect, self.npc3.rect])

        # Fantasma decorativo
        self.fantasma_positions = [
            (200, 485), (125, 855), (820, 720),
            (1920, 500), (705, 920), (1060, 485)
        ]
        self.fantasma = Fantasma(self.fantasma_positions)

        # Monstruos que siguen al jugador
        self.monsters = pygame.sprite.Group()
        self.spawn_monsters(5)  # Puedes ajustar la cantidad

        self.damage_cooldown = 1000
        self.last_damage_time = 0

        # Diálogo
        self.dialogue = None
        self.dialogue_timer = 0

    def spawn_monsters(self, count):
        for _ in range(count):
            x = random.randint(100, 1400)
            y = random.randint(100, 900)
            ghost_type = random.choice([1, 2, 3])
            monster = Monster(x, y, ghost_type)
            monster.speed = 60  # Lento para que no alcance tan fácil
            self.monsters.add(monster)

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        current_time = pygame.time.get_ticks()

        # Fantasma decorativo
        self.fantasma.update(current_time)

        # Monstruos: seguir al jugador y hacer daño
        for monster in self.monsters:
            monster.update(self.player, dt)
            if self.player.rect.colliderect(monster.rect):
                if current_time - self.last_damage_time > self.damage_cooldown:
                    self.player.health -= 10
                    self.last_damage_time = current_time
                    if self.player.health <= 0:
                        if death_screen(self.screen):
                            return "restart"
                        
        if self.player.attacking:
            attack_hitbox = self.player.get_attack_hitbox()
            for monster in self.monsters:
                if attack_hitbox.colliderect(monster.rect):
                    monster.take_damage(10)  # Aplica 10 puntos de daño al monstruo

        if self.player.health <= 0:
            death_screen(self.screen)

        # Diálogo
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.dialogue = None

        # Transiciones
        if self.player.rect.colliderect(pygame.Rect(0, 0, 10, 1000)):
            self.player.rect.center = (1460, 894)
            return "cafeteria_noche"

        if self.player.rect.colliderect(pygame.Rect(772, 964, 193, 10)):
            self.player.rect.center = (342, 118)
            return "interior_edificio_h"

        if self.player.rect.colliderect(pygame.Rect(773, 317, 192, 4)):
                self.player.rect.center = (319, 453)
                return "interior_edificio_i"

        return None

    def get_hud_visibility(self):
        return not self.dialogue

    def render(self):
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM

        camera_offset_x = max(0, min(self.player.rect.centerx - view_width / 2, self.map.fondo_rect.width - view_width))
        camera_offset_y = max(0, min(self.player.rect.centery - view_height / 2, self.map.fondo_rect.height - view_height))
        camera_offset = (camera_offset_x, camera_offset_y)

        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))

        self.map.draw_fondo(world_surface, camera_offset)

        for sprite in self.player_group:
            world_surface.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))

                # (Opcional) Dibuja el hitbox de ataque en modo depuración
        if self.player.attacking:
            attack_hitbox = self.player.get_attack_hitbox()
            world_surface.blit(
                self.player.scissors_image,
                (attack_hitbox.x - camera_offset[0],
                attack_hitbox.y - camera_offset[1])
            )

        for npc in self.npc_group:
            world_surface.blit(npc.image, (npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1]))

        if self.fantasma.visible:
            world_surface.blit(self.fantasma.image, (self.fantasma.rect.x - camera_offset[0], self.fantasma.rect.y - camera_offset[1]))

        for monster in self.monsters:
            monster.draw(world_surface, camera_offset)

        self.map.draw_primer_plano(world_surface, camera_offset)

        scaled_surface = pygame.transform.scale(world_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))

        if self.dialogue:
            draw_dialogue(self.screen, "", self.dialogue)
