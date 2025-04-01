# paths.py
import os
from settings import ASSETS_DIR

def get_asset_path(*subpaths):
    """
    Retorna la ruta absoluta al recurso ubicado dentro de la carpeta assets.
    Ejemplo: get_asset_path("items", "tijeras.png")
    """
    return os.path.join(ASSETS_DIR, *subpaths)
