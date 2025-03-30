# hud.py
import pygame
from utils import draw_health_bar, draw_hotbar


class HUD:
    def __init__(self, player):
        self.player = player
        # Suponemos que el inventario y el slot seleccionado son propiedades del jugador o se administran aquí
        self.inventory = (
            []
        )  # Puedes sincronizarlo con self.player.inventory si es necesario
        self.selected_slot = 0
        self.slot_count = 4  # Número total de slots disponibles
        self.show_inventory = True

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.selected_slot = (self.selected_slot - 1) % self.slot_count
                elif event.key == pygame.K_x:
                    self.selected_slot = (self.selected_slot + 1) % self.slot_count

    def update(self, dt):
        # Aquí podrías sincronizar self.inventory con el inventario del jugador
        pass

    def render(self, surface):

        if self.show_inventory:
            # Dibujar la barra de salud en la esquina superior izquierda
            draw_health_bar(surface, 10, 10, self.player.health, self.player.max_health)
            # Dibujar el inventario
            draw_hotbar(surface, self.inventory, self.selected_slot)
