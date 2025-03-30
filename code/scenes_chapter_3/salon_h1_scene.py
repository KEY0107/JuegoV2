import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_3.scene import Scene
from utils import draw_dialogue, draw_prompt


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, name, dialogue):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name
        self.dialogue = dialogue


class Note(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, text):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (17, 11))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text


class SalonH1Scene(Scene):
    note_taken_flag = False  # Para comunicar a otras escenas

    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("salon_h1.png")
        self.obstacles = get_collisions("salon_h1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "salon_h1"

        self.npc1 = NPC(431, 338, "../assets/characters/NPC_12.png", "Compañero", "¿Estás bien?")
        self.npc2 = NPC(491, 206, "../assets/characters/NPC_8.png", "Compañera", "Deberías ir a casa Alex, te miras mal.")
        self.npc_group = pygame.sprite.Group(self.npc1, self.npc2)

        self.obstacles.append(self.npc1.rect)
        self.obstacles.append(self.npc2.rect)

        self.note = Note(124, 220, "../assets/items/nota1.png", "Es un tonto, aún no se da cuenta.")
        self.note_visible = True
        self.note_active = False
        self.note_taken = False

        self.active_npc = None
        self.dialogue_active = False
        self.post_note_dialogue = False
        self.await_post_note_exit = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.dialogue_active:
                    self.dialogue_active = False
                    self.active_npc = None
                elif self.note_active:
                    self.note_active = False
                    self.note_visible = False
                    self.note_taken = True
                    SalonH1Scene.note_taken_flag = True
                    self.post_note_dialogue = True
                elif self.post_note_dialogue:
                    self.post_note_dialogue = False
                    self.await_post_note_exit = True
                else:
                    for npc in self.npc_group:
                        if self.player.rect.colliderect(npc.rect):
                            self.dialogue_active = True
                            self.active_npc = npc
                            return
                    if self.note_visible and self.player.rect.colliderect(self.note.rect):
                        self.note_active = True

    def update(self, dt):
        if not self.dialogue_active and not self.note_active and not self.post_note_dialogue:
            self.player.update(dt, self.obstacles)
            self.player.clamp_within_map(self.map.fondo_rect)

        door_interior_to_edificio_h2 = pygame.Rect(509, 447, 100, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_h2):
            self.player.rect.center = (722, 280)
            return "interior_edificio_h2"

        return None

    def get_hud_visibility(self):
        return not (self.dialogue_active or self.note_active or self.post_note_dialogue)

    def render(self):
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM

        camera_offset_x = self.player.rect.centerx - view_width / 2
        camera_offset_y = self.player.rect.centery - view_height / 2

        if self.map.fondo_rect.width < view_width:
            camera_offset_x = (self.map.fondo_rect.width - view_width) / 2
        else:
            camera_offset_x = max(0, min(camera_offset_x, self.map.fondo_rect.width - view_width))

        if self.map.fondo_rect.height < view_height:
            camera_offset_y = (self.map.fondo_rect.height - view_height) / 2
        else:
            camera_offset_y = max(0, min(camera_offset_y, self.map.fondo_rect.height - view_height))

        camera_offset = (camera_offset_x, camera_offset_y)
        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))

        self.map.draw_fondo(world_surface, camera_offset)

        for sprite in self.player_group:
            world_surface.blit(
                sprite.image,
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1])
            )

        for npc in self.npc_group:
            world_surface.blit(
                npc.image,
                (npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1])
            )

        if self.note_visible:
            world_surface.blit(
                self.note.image,
                (self.note.rect.x - camera_offset[0], self.note.rect.y - camera_offset[1])
            )

        self.map.draw_primer_plano(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(world_surface, (current_width, current_height))
        self.screen.blit(scaled_surface, (0, 0))

        if self.dialogue_active and self.active_npc:
            draw_dialogue(self.screen, self.active_npc.name, self.active_npc.dialogue)

        elif self.note_active:
            draw_dialogue(self.screen, "Nota", self.note.text)

        elif self.post_note_dialogue:
            draw_dialogue(self.screen, "Alex", "Me siento mal... debería ir al baño a lavarme la cara")

        if not self.dialogue_active and not self.note_active and not self.post_note_dialogue:
            for npc in self.npc_group:
                if self.player.rect.colliderect(npc.rect):
                    scale_x = current_width / view_width
                    scale_y = current_height / view_height
                    npc_screen_x = (npc.rect.centerx - camera_offset[0]) * scale_x
                    npc_screen_y = (npc.rect.top - camera_offset[1]) * scale_y
                    draw_prompt(self.screen, (npc_screen_x, npc_screen_y - 20))
            if self.note_visible and self.player.rect.colliderect(self.note.rect):
                scale_x = current_width / view_width
                scale_y = current_height / view_height
                note_screen_x = (self.note.rect.centerx - camera_offset[0]) * scale_x
                note_screen_y = (self.note.rect.top - camera_offset[1]) * scale_y
                draw_prompt(self.screen, (note_screen_x, note_screen_y - 20))
