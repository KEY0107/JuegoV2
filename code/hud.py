# hud.py
import pygame
from utils import draw_health_bar, draw_hotbar


class HUD:
    def __init__(self, player):
        self.player = player
        # Suponemos que el inventario y el slot seleccionado son propiedades del jugador o se administran aquí
        self.inventory = (
            []
        )  # Por ejemplo, puedes sincronizarlo con el inventario del jugador
        self.selected_slot = 0

    def update(self, dt):
        # Si se producen eventos que afecten la salud o el inventario, actualízalos aquí
        # Por ejemplo, podrías sincronizar self.inventory con self.player.inventory
        pass

    def render(self, surface):
        # Dibujar la barra de salud en la esquina superior izquierda (o donde prefieras)
        draw_health_bar(surface, 10, 10, self.player.health, self.player.max_health)
        # Dibujar la hotbar en la parte inferior
        draw_hotbar(surface, self.inventory, self.selected_slot)
