import pygame
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene
import globales_chapter_1
from npc import NPC
from utils import draw_dialogue, draw_prompt
import conversaciones_chapter1


class InteriorEdificioI2(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.map = Map("pasillo_i2.png")
        self.obstacles = get_collisions("hallway_i2")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("hallway.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_edificio_i2"
        # Crear el NPC de la tutora Marian en (348, 327)
        self.marian_npc = NPC(348, 327, "marian_frente.png", "Marian", "")

        # Variables para gestionar la conversación directa con Marian
        self.conversation_active = False
        self.conversation_lines = []
        self.conversation_line_index = 0
        self.conversation_cooldown = 0

        # --- Variables para el evento del fantasma ---
        # Zona que dispara el evento (tras la conversación con Marian)
        self.ghost_event_trigger_rect = pygame.Rect(284, 429, 105, 7)
        # Punto donde se crea el NPC fantasma
        self.ghost_spawn_point = (956, 304)
        # Zona para que el fantasma desaparezca
        self.ghost_disappear_rect = pygame.Rect(789, 267, 5, 86)
        self.ghost_event_triggered = False
        self.ghost_event_timer = 0  # Duración del audio
        self.ghost_audio_played = False
        self.fantasma_npc = None
        self.ghost_dialogue_active = False  # Para mostrar el diálogo de Alex
        self.ghost_dialogue_shown = False

        try:
            self.puerta_sound = pygame.mixer.Sound(
                "../assets/sound/puerta_cerrandose.mp3"
            )
        except Exception as e:
            print("Error loading puerta_cerrandose.mp3:", e)
            self.puerta_sound = None

    def handle_events(self, events):
        # Procesar el avance del diálogo de Marian
        if self.conversation_active:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.conversation_line_index += 1
                    if self.conversation_line_index >= len(self.conversation_lines):
                        self.conversation_active = False
                        if not globales_chapter_1.MARIAN_CONVERSATION_DONE:
                            globales_chapter_1.MARIAN_CONVERSATION_DONE = True
                        self.conversation_lines = []
                        self.conversation_line_index = 0
        # Procesar el diálogo del evento del fantasma (de Alex)
        if self.ghost_dialogue_active:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.ghost_dialogue_active = False
                    self.ghost_dialogue_shown = True

    def update(self, dt):
        # Si hay conversación activa (con Marian o del fantasma), no se actualiza la lógica normal
        if self.conversation_active or self.ghost_dialogue_active:
            return None

        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Transiciones de la escena
        door_interior_to_edificio_i = pygame.Rect(290, 479, 95, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_i):
            self.player.rect.center = (347, 85)
            return "interior_edificio_i"
        door_interior_to_salon_i2 = pygame.Rect(931, 351, 49, 5)
        if self.player.rect.colliderect(door_interior_to_salon_i2):
            self.player.rect.center = (539, 122)
            return "salon_i2"

        # Interacción con la tutora Marian
        if globales_chapter_1.MARIAN_VISIBLE and self.player.rect.colliderect(
            self.marian_npc.rect
        ):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self.conversation_cooldown <= 0:
                self.conversation_active = True
                self.conversation_line_index = 0
                if not globales_chapter_1.MARIAN_CONVERSATION_DONE:
                    self.conversation_lines = (
                        conversaciones_chapter1.CONVERSACION_TUTORA_MARIAN
                    )
                else:
                    self.conversation_lines = (
                        conversaciones_chapter1.CONVERSACION_TUTORA_MARIAN_SIMPLE
                    )
                self.conversation_cooldown = 500
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= dt

        # --- Evento del fantasma ---
        # Solo se dispara si ya se completó la conversación con Marian y el evento aún no se ha completado globalmente
        if (
            globales_chapter_1.MARIAN_CONVERSATION_DONE
            and not globales_chapter_1.EVENT_FANTASMA_DONE
        ):
            # Paso 1: Disparar el evento cuando el jugador se acerque a la zona
            if not self.ghost_event_triggered and self.player.rect.colliderect(
                self.ghost_event_trigger_rect
            ):
                self.ghost_event_triggered = True
                self.ghost_event_timer = 3000  # 3 segundos de audio
                if self.puerta_sound:
                    self.puerta_sound.play()
                self.ghost_audio_played = True

            # Paso 2: Mientras el audio se reproduce, decrementar el temporizador
            if (
                self.ghost_event_triggered
                and self.ghost_audio_played
                and self.ghost_event_timer > 0
            ):
                self.ghost_event_timer -= dt
            # Paso 3: Una vez finalizado el audio, crear el NPC fantasma si no existe
            if (
                self.ghost_event_triggered
                and self.ghost_audio_played
                and self.ghost_event_timer <= 0
                and self.fantasma_npc is None
            ):
                self.fantasma_npc = NPC(
                    self.ghost_spawn_point[0],
                    self.ghost_spawn_point[1],
                    "fantasma_frente.png",
                    "Fantasma",
                    "",
                )
                self.fantasma_npc.visible = True
                self.fantasma_npc.interactable = False
            # Paso 4: Activar el diálogo de Alex si el fantasma está presente y aún no se mostró
            if (
                self.fantasma_npc
                and not self.ghost_dialogue_shown
                and not self.ghost_dialogue_active
            ):
                self.ghost_dialogue_active = True
            # Paso 5: Cuando el diálogo ya se mostró y el jugador se acerca a la zona de desaparición,
            # ocultar el fantasma y marcar el evento como completado globalmente.
            if (
                self.fantasma_npc
                and self.ghost_dialogue_shown
                and self.player.rect.colliderect(self.ghost_disappear_rect)
            ):
                self.fantasma_npc.visible = False
                globales_chapter_1.EVENT_FANTASMA_DONE = True

        return None

    def get_hud_visibility(self):
        # Ocultar el HUD mientras se muestra el diálogo de Alex o Marian
        if self.ghost_dialogue_active or self.conversation_active:
            return False
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
        # Dibujar el NPC de Marian si es visible
        if globales_chapter_1.MARIAN_VISIBLE:
            self.marian_npc.draw(world_surface, camera_offset)
        # Dibujar el fantasma si existe y es visible
        if self.fantasma_npc and self.fantasma_npc.visible:
            self.fantasma_npc.draw(world_surface, camera_offset)

        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Mostrar prompt de interacción para Marian si el jugador está cerca y no hay conversación activa
        if (
            globales_chapter_1.MARIAN_VISIBLE
            and not self.conversation_active
            and self.player.rect.colliderect(self.marian_npc.rect)
        ):
            npc_screen_x = self.marian_npc.rect.centerx - camera_offset[0]
            npc_screen_y = self.marian_npc.rect.top - camera_offset[1]
            prompt_pos = (npc_screen_x, npc_screen_y - 20)
            draw_prompt(self.screen, prompt_pos)

        # Mostrar diálogo de la conversación con Marian
        if self.conversation_active:
            speaker, text = self.conversation_lines[self.conversation_line_index]
            draw_dialogue(self.screen, speaker, text)

        # Mostrar diálogo del evento del fantasma (de Alex)
        if self.ghost_dialogue_active:
            draw_dialogue(
                self.screen, "Alex", "¿Se escuchó en el último salón? Voy a ir a ver"
            )
