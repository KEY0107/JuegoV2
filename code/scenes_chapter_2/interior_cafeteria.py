import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_1.scene import Scene
from utils import draw_dialogue, draw_prompt

class Note(pygame.sprite.Sprite):
    def _init_(self, x, y, image_path, text, note_flag):
        super()._init_()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (17, 11))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text
        self.note_flag = note_flag  # flag para saber si la nota ha sido tomada


class InteriorCafeteriaScene(Scene):
    note_taken_flag = False  # Atributo estático para la bandera de la nota tomada

    def _init_(self, screen, player):
        super()._init_(screen)
        # Cargar los assets del interior de la cafetería
        self.map = Map("interior_cafeteria.png", "cafeteria_interior_objetos.png")
        # Se asume que las colisiones están definidas con la clave "interior_cafeteria"
        self.obstacles = get_collisions("interior_cafeteria")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_cafeteria"

        # Crear la nueva nota en la posición deseada
        self.note = Note(544, 288, "../assets/items/nota2.png", 
                         "Se que te Preocupas por mi, pero estoy bien.\n"
                         " Oye, ya basta. Me incomoda que me observes todo el tiempo", 
                         InteriorCafeteriaScene.note_taken_flag)
        self.note_visible = True
        self.note_active = False
        self.note_taken = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.note_active:
                    self.note_active = False
                    self.note_visible = False
                    # Marcar la nota como tomada
                    InteriorCafeteriaScene.note_taken_flag = True
                elif self.note_visible and self.player.rect.colliderect(self.note.rect):
                    self.note_active = True

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)
        # Transición para ir a la cafetería
        door_interior_to_cafeteria = pygame.Rect(632, 493, 90, 10)
        if self.player.rect.colliderect(door_interior_to_cafeteria):
            self.player.rect.center = (540, 438)
            return "cafeteria_noche"
        return None

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

        # Dibujar la nota solo si aún no ha sido tomada
        if self.note_visible and not InteriorCafeteriaScene.note_taken_flag:
            world_surface.blit(
                self.note.image,
                (self.note.rect.x - camera_offset[0], self.note.rect.y - camera_offset[1])
            )

        self.map.draw_primer_plano(world_surface, camera_offset)
        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        if self.note_active:
            draw_dialogue(self.screen, "Nota", self.note.text)

        if not self.note_active:
            scale_x = current_width / view_width
            scale_y = current_height / view_height
            note_screen_x = (self.note.rect.centerx - camera_offset[0]) * scale_x
            note_screen_y = (self.note.rect.top - camera_offset[1]) * scale_y
            draw_prompt(self.screen, (note_screen_x, note_screen_y - 20))