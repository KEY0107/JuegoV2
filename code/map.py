# map.py
import pygame
import os
from settings import MAPS_DIR

class Map:
    def __init__(self, fondo_path, primer_plano_path=None):
        # Carga del fondo (mapa sin elementos de primer plano)
        self.fondo = pygame.image.load(os.path.join(MAPS_DIR, fondo_path)).convert()
        self.fondo_rect = self.fondo.get_rect()
        # Carga de la capa superior si se proporciona
        self.primer_plano = None
        if primer_plano_path is not None:
            self.primer_plano = pygame.image.load(os.path.join(MAPS_DIR, primer_plano_path)).convert_alpha()
            self.primer_plano_rect = self.primer_plano.get_rect()

    def draw_fondo(self, surface, camera_offset):
        surface.blit(self.fondo, (-camera_offset[0], -camera_offset[1]))

    def draw_primer_plano(self, surface, camera_offset):
        if self.primer_plano:
            surface.blit(self.primer_plano, (-camera_offset[0], -camera_offset[1]))
