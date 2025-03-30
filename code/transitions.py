# transitions.py
import pygame

class TransitionManager:
    def __init__(self, screen_size, fade_speed=5):
        self.fade_surface = pygame.Surface(screen_size)
        self.fade_surface.fill((0, 0, 0))
        self.fade_speed = fade_speed
        self.alpha = 0
        self.state = None  # Puede ser None, "fade_out" o "fade_in"

    def start_fade_out(self):
        self.state = "fade_out"
        self.alpha = 0

    def start_fade_in(self):
        self.state = "fade_in"
        self.alpha = 255

    def update(self):
        if self.state == "fade_out":
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
        elif self.state == "fade_in":
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = None

    def draw(self, surface):
        if self.state is not None:
            self.fade_surface.set_alpha(self.alpha)
            surface.blit(self.fade_surface, (0, 0))
