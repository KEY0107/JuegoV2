import pygame
import os
from settings import ASSETS_DIR


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image_filename, name, dialogue):
        super().__init__()
        original_image = pygame.image.load(
            os.path.join(ASSETS_DIR, "characters", image_filename)
        ).convert_alpha()
        original_width, original_height = original_image.get_size()
        desired_height = 70  # Por ejemplo
        aspect_ratio = original_width / original_height
        desired_width = int(desired_height * aspect_ratio)
        self.image = pygame.transform.scale(
            original_image, (desired_width, desired_height)
        )
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name
        self.dialogue = dialogue
        self.dialogue_active = False
        self.visible = True  # Controla la visibilidad
        self.interactable = True  # Por defecto, se puede interactuar

    def draw(self, surface, camera_offset):
        if self.visible:
            surface.blit(
                self.image,
                (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]),
            )

    def start_dialogue(self):
        if self.interactable:
            self.dialogue_active = True

    def stop_dialogue(self):
        self.dialogue_active = False
