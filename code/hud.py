import pygame
import os
from utils import draw_health_bar, draw_hotbar
from inventory_item import InventoryItem

class HUD:
    def __init__(self, player):
        self.player = player
        self.inventory = []
        self.selected_slot = 0
        self.slot_count = 4
        self.show_inventory = True

        # ✅ Añadir el objeto inicial: "tijeras"
        try:
            tijeras_image = pygame.image.load("/assets/items/tijeras.png").convert_alpha()
            tijeras_image = pygame.transform.scale(tijeras_image, (50, 50))
            self.inventory.append(InventoryItem(tijeras_image, "tijeras"))  # ✅ le damos nombre
        except Exception as e:
            print("No se pudo cargar la imagen de tijeras:", e)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.selected_slot = (self.selected_slot - 1) % self.slot_count
                elif event.key == pygame.K_x:
                    self.selected_slot = (self.selected_slot + 1) % self.slot_count

    def update(self, dt):
        pass

    def render(self, surface):
        if self.show_inventory:
            draw_health_bar(surface, 10, 10, self.player.health, self.player.max_health)
            draw_hotbar(surface, self.inventory, self.selected_slot)
