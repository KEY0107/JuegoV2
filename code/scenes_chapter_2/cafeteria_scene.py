import pygame
import random
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from monster import Monster
from death import death_screen  # Asegúrate de tenerlo importado
import sys

# Variable global para controlar si el mensaje de miedo se mostró o no
first_time_message_shown = True

class CafeteriaScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("cafeteria_noche.png", "cafeteria_noche_objetos.png")
        self.obstacles = get_collisions("cafeteria")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "cafeteria_noche"

        # Grupo de monstruos
        self.monsters = pygame.sprite.Group()
        self.spawn_monsters(5)

        self.damage_cooldown = 1000  # Tiempo entre daños (ms)
        self.last_damage_time = 0

    def spawn_monsters(self, count):
        for _ in range(count):
            x = random.randint(200, 1200)
            y = random.randint(200, 600)
            ghost_type = random.choice([1, 2, 3])
            monster = Monster(x, y, ghost_type)
            monster.speed = 60  # Más lento para que no te alcancen fácilmente
            self.monsters.add(monster)

    def show_scared_message(self):
        # Mostrar el mensaje de miedo como un diálogo en la parte inferior de la pantalla
        font = pygame.font.SysFont("arial", 24)
        scared_message = "¿Qué es eso? Me estoy volviendo loco..."
        text = font.render(scared_message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))

        # Fondo oscuro para el mensaje
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, self.screen.get_height() - 100, self.screen.get_width(), 100))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_e):
                        waiting_for_input = False

    def handle_events(self, events):
        pass

    def update(self, dt):
        global first_time_message_shown

        if first_time_message_shown:
            self.show_scared_message()
            first_time_message_shown = False

        # Actualiza al jugador y limita su movimiento dentro del mapa
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Si el jugador está atacando, verifica colisiones entre el hitbox de ataque y los monstruos
        if self.player.attacking:
            attack_hitbox = self.player.get_attack_hitbox()
            for monster in self.monsters:
                if attack_hitbox.colliderect(monster.rect):
                    monster.take_damage(10)  # Aplica 10 puntos de daño

        current_time = pygame.time.get_ticks()
        for monster in self.monsters:
            monster.update(self.player, dt)
            # Si el jugador colisiona con el monstruo, se le aplica daño al jugador
            if self.player.rect.colliderect(monster.rect):
                if current_time - self.last_damage_time > self.damage_cooldown:
                    self.player.health -= 10
                    self.last_damage_time = current_time
                    if self.player.health <= 0:
                        if death_screen(self.screen):  # Si el jugador presiona R, por ejemplo
                            return "restart"

        # Transiciones de escena
        if self.player.rect.colliderect(pygame.Rect(0, 0, 10, 1000)):
            self.player.rect.center = (1300, 100)
            return "entrada_noche"
        if self.player.rect.colliderect(pygame.Rect(1490, 0, 10, 1000)):
            self.player.rect.center = (70, 693)
            return "jardineras_noche"
        if self.player.rect.colliderect(pygame.Rect(484, 400, 112, 10)):
            self.player.rect.center = (670, 456)
            return "interior_cafeteria"

        return None

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

        # Dibuja al jugador
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

        # Dibuja los monstruos
        for monster in self.monsters:
            monster.draw(world_surface, camera_offset)

        self.map.draw_primer_plano(world_surface, camera_offset)

        scaled_surface = pygame.transform.scale(world_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
