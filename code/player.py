import pygame
import os
from settings import CHARACTERS_DIR
from inventory_item import InventoryItem


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations = {
            "down": [pygame.image.load(os.path.join(CHARACTERS_DIR, f"down_{i}.png")).convert_alpha() for i in range(4)],
            "up": [pygame.image.load(os.path.join(CHARACTERS_DIR, f"up_{i}.png")).convert_alpha() for i in range(4)],
            "left": [pygame.image.load(os.path.join(CHARACTERS_DIR, f"left_{i}.png")).convert_alpha() for i in range(4)],
            "right": [pygame.image.load(os.path.join(CHARACTERS_DIR, f"right_{i}.png")).convert_alpha() for i in range(4)],
        }
        self.direction = "down"
        self.frame_index = 0
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

        self.health = 100
        self.max_health = 100
        self.animation_timer = 0
        self.animation_speed = 350
        self.is_moving = False

        self.attacking = False
        self.attack_duration = 200
        self.attack_timer = 0

        self.attack_left_sprite = pygame.image.load(os.path.join(CHARACTERS_DIR, "attack_left.png")).convert_alpha()
        self.attack_right_sprite = pygame.image.load(os.path.join(CHARACTERS_DIR, "attack_right.png")).convert_alpha()
        self.attack_up_sprite = pygame.image.load(os.path.join(CHARACTERS_DIR, "attack_up.png")).convert_alpha()
        self.attack_down_sprite = pygame.image.load(os.path.join(CHARACTERS_DIR, "attack_down.png")).convert_alpha()

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None

        self.hud = None  # Se asignará externamente

    def update(self, dt, obstacles):
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False

            if self.direction == "left":
                self.image = self.attack_left_sprite
            elif self.direction == "right":
                self.image = self.attack_right_sprite
            elif self.direction == "up":
                self.image = self.attack_up_sprite
            elif self.direction == "down":
                self.image = self.attack_down_sprite
            return

        self.handle_input(obstacles)
        self.animation_timer += dt
        if self.is_moving:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
                self.image = self.animations[self.direction][self.frame_index]
        else:
            self.frame_index = 0
            self.image = self.animations[self.direction][self.frame_index]

    def attack(self):
        self.attacking = True
        self.attack_timer = self.attack_duration

    def handle_input(self, obstacles):
        if self.joystick:
            self.handle_joystick(obstacles)
        else:
            self.handle_keys(obstacles)

    def handle_keys(self, obstacles):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        self.is_moving = False

        # Movimiento
        if keys[pygame.K_a]:
            dx = -self.speed
            self.direction = "left"
            self.is_moving = True
        if keys[pygame.K_d]:
            dx = self.speed
            self.direction = "right"
            self.is_moving = True
        if keys[pygame.K_w]:
            dy = -self.speed
            self.direction = "up"
            self.is_moving = True
        if keys[pygame.K_s]:
            dy = self.speed
            self.direction = "down"
            self.is_moving = True

        # Ataque con tijeras
        if keys[pygame.K_SPACE] and not self.attacking:
            if self.hud and 0 <= self.hud.selected_slot < len(self.hud.inventory):
                item = self.hud.inventory[self.hud.selected_slot]
                if isinstance(item, InventoryItem) and item.name.lower() == "tijeras":
                    self.attack()

        self.move_and_collide(dx, dy, obstacles)

    def handle_joystick(self, obstacles):
        axis_y = self.joystick.get_axis(0)
        axis_x = -self.joystick.get_axis(1)
        dead_zone = 0.1
        dx, dy = 0, 0
        self.is_moving = False

        if abs(axis_x) > dead_zone:
            dx = axis_x * self.speed
            self.direction = "right" if axis_x > 0 else "left"
            self.is_moving = True
        if abs(axis_y) > dead_zone:
            dy = axis_y * self.speed
            self.direction = "down" if axis_y > 0 else "up"
            self.is_moving = True

        self.move_and_collide(dx, dy, obstacles)

    def move_and_collide(self, dx, dy, obstacles):
        self.rect.x += dx
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right

        self.rect.y += dy
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dy > 0:
                    self.rect.bottom = obstacle.top
                elif dy < 0:
                    self.rect.top = obstacle.bottom

    def clamp_within_map(self, map_rect):
        if self.rect.left < map_rect.left:
            self.rect.left = map_rect.left
        if self.rect.right > map_rect.right:
            self.rect.right = map_rect.right
        if self.rect.top < map_rect.top:
            self.rect.top = map_rect.top
        if self.rect.bottom > map_rect.bottom:
            self.rect.bottom = map_rect.bottom
