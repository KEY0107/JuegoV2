import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
import globales_chapter_1


class SalonI2(Scene):
    def _init_(self, screen, player):
        super()._init_(screen)
        self.map = Map("salon_i2.png")
        self.obstacles = get_collisions("salon_i2")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "salon_i2"

        # --- Nota en el salón ---
        # La nota solo aparecerá si aún no fue tomada (global)
        if not globales_chapter_1.NOTA_SALON_TAKEN:
            try:
                self.note_img = pygame.image.load(
                    "/assets/items/nota2.png"
                ).convert_alpha()
                self.note_img = pygame.transform.scale(self.note_img, (20, 20))
            except Exception as e:
                print("Error loading nota2.png:", e)
                self.note_img = None
            # Posición de la nota en el salón (ajusta según convenga)
            if self.note_img:
                self.note_rect = self.note_img.get_rect(topleft=(400, 300))
            else:
                self.note_rect = pygame.Rect(400, 300, 20, 20)
        else:
            self.note_img = None

        self.note_triggered = False

    def handle_events(self, events):
        # Procesar la interacción con la nota
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                # Activar la interacción con la nota (solo si aún no se ha tomado)
                if not self.note_triggered and self.note_img and self.player.rect.colliderect(self.note_rect):
                    self.note_triggered = True
                    # Marcar la nota como tomada
                    globales_chapter_1.NOTA_SALON_TAKEN = True
                    # Activar visibilidad de Gael
                    globales_chapter_1.GAEL_VISIBLE = True
                    globales_chapter_1.GAEL_CONVERSATION_UNLOCKED = True

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Transición: regresar a interior_edificio_i2
        door_interior_to_edificio_i2 = pygame.Rect(514, 23, 49, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_i2):
            self.player.rect.center = (955, 318)
            return "interior_edificio_i2"

        return None

    def get_hud_visibility(self):
        # El HUD se mantiene visible cuando no hay interacción con la nota
        return True

    def render(self):
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM
        camera_offset_x = self.player.rect.centerx - view_width / 2
        camera_offset_y = self.player.rect.centery - view_height / 2
        if self.map.fondo_rect.width < view_width:
            camera_offset_x = (self.map.fondo_rect.width - view_width) / 2
        else:
            camera_offset_x = max(
                0, min(camera_offset_x, self.map.fondo_rect.width - view_width)
            )
        if self.map.fondo_rect.height < view_height:
            camera_offset_y = (self.map.fondo_rect.height - view_height) / 2
        else:
            camera_offset_y = max(
                0, min(camera_offset_y, self.map.fondo_rect.height - view_height)
            )
        camera_offset = (camera_offset_x, camera_offset_y)

        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))
        self.map.draw_fondo(world_surface, camera_offset)
        for sprite in self.player_group:
            world_surface.blit(
                sprite.image,
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]),
            )
        self.map.draw_primer_plano(world_surface, camera_offset)

        # Dibujar la nota solo si aún no ha sido tomada (global)
        if self.note_img and not globales_chapter_1.NOTA_SALON_TAKEN:
            world_surface.blit(
                self.note_img,
                (
                    self.note_rect.x - camera_offset[0],
                    self.note_rect.y - camera_offset[1],
                ),
            )

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))