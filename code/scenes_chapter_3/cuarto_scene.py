import pygame
from map import Map
from collision_data import get_collisions
from player import Player
from sound_manager import SoundManager
from utils import draw_dialogue
from scenes_chapter_3.scene import Scene
from scenes_chapter_3.salon_h1_scene import SalonH1Scene  # Para verificar si se recogió la nota


class CuartoScene(Scene):
    first_time_shown = False

    def __init__(self, screen, show_initial_dialogue=True, player=None):
        super().__init__(screen)
        self.map = Map("casa_alex_cuarto.png")
        self.obstacles = get_collisions("casa_alex_cuarto")
        self.player = Player(180, 170) if player is None else player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("ambience.mp3", fade_in_ms=1000)
        self.DEFAULT_ZOOM = 2
        self.current_map = "casa_alex_cuarto"
        self.initial_dialogue_active = show_initial_dialogue
        self.initial_dialogue_text = "¿Qué fue eso...? ¿Necesitaré hablar con alguien?"

        self.extra_dialogues = []
        self.current_extra_dialogue = 0
        self.extra_dialogue_active = False
        self.chapter_end = False  # Controla si se muestra el fin de capítulo

        # Cinemática de entrada (pantalla negra y sonido de susto)
        if not CuartoScene.first_time_shown:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.time.delay(1000)

            susto_sound = pygame.mixer.Sound("/assets/sound/susto.mp3")
            susto_channel = susto_sound.play()
            pygame.time.delay(3000)
            susto_channel.stop()

            CuartoScene.first_time_shown = True

        # Si la nota fue tomada, activar diálogos extra y sonido de llanto
        if SalonH1Scene.note_taken_flag:
            llanto_sound = pygame.mixer.Sound("/assets/sound/llanto.mp3")
            self.llanto_channel = llanto_sound.play(-1)  # Reproducir en bucle
            self.extra_dialogues = [
                "Tengo que hacerlo... si lo hago ella descansará y todo volverá a la normalidad.",
                "Gael sabe algo y debo descubrir qué es."
            ]
            self.extra_dialogue_active = True

    def get_hud_visibility(self):
        return not (self.initial_dialogue_active or self.extra_dialogue_active or self.chapter_end)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.initial_dialogue_active and event.key == pygame.K_e:
                    self.initial_dialogue_active = False
                elif self.extra_dialogue_active and event.key == pygame.K_e:
                    self.current_extra_dialogue += 1
                    if self.current_extra_dialogue >= len(self.extra_dialogues):
                        self.extra_dialogue_active = False
                        if hasattr(self, 'llanto_channel'):
                            self.llanto_channel.stop()
                        self.chapter_end = True  # Activar fin de capítulo

    def update(self, dt):
        if not self.initial_dialogue_active and not self.extra_dialogue_active and not self.chapter_end:
            self.player.update(dt, self.obstacles)
            self.player.clamp_within_map(self.map.fondo_rect)

        door_cuarto_to_sala = pygame.Rect(0, 235, 10, 40)
        if self.player.rect.colliderect(door_cuarto_to_sala):
            self.player.rect.center = (880, 165)
            return "sala"
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
                (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]),
            )

        self.map.draw_primer_plano(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(world_surface, (current_width, current_height))
        self.screen.blit(scaled_surface, (0, 0))

        if self.initial_dialogue_active:
            draw_dialogue(
                self.screen,
                "Alex",
                self.initial_dialogue_text,
                "Alex_triste_conversation",
            )

        elif self.extra_dialogue_active and self.current_extra_dialogue < len(self.extra_dialogues):
            draw_dialogue(
                self.screen,
                "Alex",
                self.extra_dialogues[self.current_extra_dialogue],
                "Alex_triste_conversation",
            )

        elif self.chapter_end:
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont("arial", 48, bold=True)
            text_surface = font.render("Fin del Capítulo 3", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(current_width // 2, current_height // 2))
            self.screen.blit(text_surface, text_rect)
            pygame.display.flip()
