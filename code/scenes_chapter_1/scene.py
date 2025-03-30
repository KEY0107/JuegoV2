import pygame


class Scene:
    def __init__(self, screen):
        self.screen = screen

    def handle_events(self, events):
        pass

    def update(self, dt):
        # Retorna None si no hay transición o una cadena con el id de la nueva escena
        return None

    def get_hud_visibility(self):
        return True

    def render(self):
        pass
