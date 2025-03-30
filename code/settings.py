# settings.py
import os

# Tamaño de la pantalla y FPS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAPS_DIR = os.path.join(ASSETS_DIR, "maps")
CHARACTERS_DIR = os.path.join(ASSETS_DIR, "characters")
SOUND_DIR = os.path.join(ASSETS_DIR, "sound")
