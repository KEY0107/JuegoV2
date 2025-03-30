import pygame


# Definición de la clase Item
class Item(pygame.sprite.Sprite):
    def __init__(self, image_filename, x, y):
        super().__init__()
        original_image = pygame.image.load(image_filename).convert_alpha()
        # Escalar la imagen a 50x50 para su representación en el mundo
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface, camera_offset):
        surface.blit(
            self.image, (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        )
