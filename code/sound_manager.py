# sound_manager.py
import pygame
from settings import SOUND_DIR
import os

class SoundManager:
    def __init__(self):
        pass

    def play_background(self, filename, fade_in_ms=1000, fade_out_ms=100):
        # Desvanecer la música actual y reproducir la nueva
        pygame.mixer.music.fadeout(fade_out_ms)
        path = os.path.join(SOUND_DIR, filename)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1, fade_ms=fade_in_ms)

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

