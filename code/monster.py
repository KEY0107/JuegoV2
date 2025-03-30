import math
import random
import pygame


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, ghost_type):
        super().__init__()
        self.ghost_type = ghost_type
        # Carga las imágenes según el tipo de espectro
        if ghost_type == 1:
            # Espectro 1: se usan imágenes distintas para cada dirección
            image_front = pygame.image.load(
                "../assets/monstruo/espectro1_espalda1.png"
            ).convert_alpha()
            image_down = pygame.image.load(
                "../assets/monstruo/espectro1_frente1.png"
            ).convert_alpha()
            image_right = pygame.image.load(
                "../assets/monstruo/espectro1_derecha1.png"
            ).convert_alpha()
            image_left = pygame.image.load(
                "../assets/monstruo/espectro1_izquierda1.png"
            ).convert_alpha()
            self.images = {
                "up": image_front,
                "down": image_down,
                "right": image_right,
                "left": image_left,
            }
        elif ghost_type == 2:
            # Espectro 2: se utiliza la misma imagen para todas las direcciones
            image_front = pygame.image.load(
                "../assets/monstruo/espectro3_espalda1.png"
            ).convert_alpha()
            image_down = pygame.image.load(
                "../assets/monstruo/espectro3_frente1.png"
            ).convert_alpha()
            image_right = pygame.image.load(
                "../assets/monstruo/espectro3_derecha1.png"
            ).convert_alpha()
            image_left = pygame.image.load(
                "../assets/monstruo/espectro3_izquierda1.png"
            ).convert_alpha()
            self.images = {
                "up": image_front,
                "down": image_down,
                "right": image_right,
                "left": image_left,
            }
        elif ghost_type == 3:
            # Espectro 3: similar al 2
            image_front = pygame.image.load(
                "../assets/monstruo/espectro4_espalda1.png"
            ).convert_alpha()
            image_down = pygame.image.load(
                "../assets/monstruo/espectro4_frente1.png"
            ).convert_alpha()
            image_right = pygame.image.load(
                "../assets/monstruo/espectro4_derecha1.png"
            ).convert_alpha()
            image_left = pygame.image.load(
                "../assets/monstruo/espectro4_izquierda1.png"
            ).convert_alpha()
            self.images = {
                "up": image_front,
                "down": image_down,
                "right": image_right,
                "left": image_left,
            }
        else:
            # Por defecto: se usa una imagen básica
            image_front = pygame.image.load(
                "../assets/monstruo/monstruo_arriba.png"
            ).convert_alpha()
            image_down = pygame.image.load(
                "../assets/monstruo/monstruo_abajo.png"
            ).convert_alpha()
            image_right = pygame.image.load(
                "../assets/monstruo/monstruo_derecha.png"
            ).convert_alpha()
            image_left = pygame.image.load(
                "../assets/monstruo/monstruo_izquierda.png"
            ).convert_alpha()
            self.images = {
                "up": image_front,
                "down": image_down,
                "right": image_right,
                "left": image_left,
            }

        # Configuración inicial
        self.direction = "up"
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 120  # velocidad en píxeles por segundo
        self.health = 150
        self.max_health = 150

    def update(self, player, dt):
        # Calcula el vector hacia el jugador
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
        # Actualiza la posición (dt está en milisegundos)
        self.rect.x += dx * self.speed * (dt / 1000)
        self.rect.y += dy * self.speed * (dt / 1000)
        # Selecciona la dirección según la componente mayor
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "up" if dy < 0 else "down"
        self.image = self.images[self.direction]

    def draw(self, surface, camera_offset):
        # Dibuja el monstruo y su barra de vida sin el contorno azul
        surface.blit(
            self.image, (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        )
        bar_width = self.rect.width
        bar_height = 5
        fill_width = int((self.health / self.max_health) * bar_width)
        bar_x = self.rect.x - camera_offset[0]
        bar_y = self.rect.y - camera_offset[1] - 10
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))
