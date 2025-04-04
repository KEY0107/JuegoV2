import pygame
import random
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene
from npc import NPC
from utils import draw_dialogue, draw_prompt
import conversaciones_chapter1
import globales_chapter_1


class SalonH1Scene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        # Cargar los assets para el interior del edificio H (pasillo segundo piso)
        self.map = Map("salon_h1.png")
        self.obstacles = get_collisions("salon_h1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("salon.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "salon_h1"
        # Variables para el evento de fin de clase
        self.class_event_active = (
            False  # Evento de fin de clase (pantalla negra con "Fin de clase")
        )
        self.class_event_triggered = False  # Se activa solo una vez
        self.class_event_timer = 0  # Duración del evento de fin de clase (ms)
        # Evento celular: una vez finalizada la clase, se muestra la imagen del celular
        self.cellphone_event_active = False
        self.cellphone_event_timer = 0  # Duración del evento celular (ms)
        # Cargar el sonido del aula
        self.classroom_sound = pygame.mixer.Sound("../assets/sound/classroom.mp3")

        # Crear múltiples NPCs
        self.npcs = [
            NPC(586, 202, "NPC_17.png", "Marcos", ""),
            NPC(426, 282, "NPC_18.png", "Carlos", ""),
        ]

        # Estados individuales para cada NPC
        self.npc_states = {}
        for npc in self.npcs:
            self.npc_states[npc] = {
                "conversation_active": False,
                "conversation_lines": [],
                "conversation_line_index": 0,
                "conversation_cooldown": 0,
            }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for npc in self.npcs:
                    state = self.npc_states[npc]
                    if state["conversation_active"]:
                        state["conversation_line_index"] += 1
                        if state["conversation_line_index"] >= len(
                            state["conversation_lines"]
                        ):
                            state["conversation_active"] = False
                            state["conversation_lines"] = []
                            state["conversation_line_index"] = 0
                            state["conversation_cooldown"] = 5000

    def update(self, dt):
        # Si estamos en el evento de fin de clase, actualizar su temporizador
        if self.class_event_active:
            self.class_event_timer -= dt
            if self.class_event_timer <= 0:
                self.class_event_active = False
                # Al finalizar, desbloqueamos la zona de interior_edificio_i globalmente
                globales_chapter_1.INTERIOR_EDIFICIO_I_AVAILABLE = True
                # Activamos el evento celular para mostrar el mensaje
                self.cellphone_event_active = True
                self.cellphone_event_timer = 4000  # 4 segundos
            return (
                None  # Durante el evento de clase, se congela la actualización normal
            )

        # Si está activo el evento celular, actualizamos su temporizador
        if self.cellphone_event_active:
            self.cellphone_event_timer -= dt
            if self.cellphone_event_timer <= 0:
                self.cellphone_event_active = False
                # Al finalizar, desbloqueamos la nota globalmente
                globales_chapter_1.NOTA_UNLOCKED = True
            return None  # Durante el evento celular, se congela la actualización normal

        for npc in self.npcs:
            state = self.npc_states[npc]
            if state["conversation_cooldown"] > 0:
                state["conversation_cooldown"] -= dt

        if not any(self.npc_states[npc]["conversation_active"] for npc in self.npcs):
            self.player.update(dt, self.obstacles)
            self.player.clamp_within_map(self.map.fondo_rect)

        keys = pygame.key.get_pressed()
        for npc in self.npcs:
            state = self.npc_states[npc]
            if (
                self.player.rect.colliderect(npc.rect)
                and keys[pygame.K_e]
                and state["conversation_cooldown"] <= 0
                and not state["conversation_active"]
                and not any(s["conversation_active"] for s in self.npc_states.values())
            ):
                state["conversation_active"] = True
                state["conversation_lines"] = random.choice(
                    conversaciones_chapter1.CONVERSACIONES_NPCS
                )
                state["conversation_line_index"] = 0
                state["conversation_cooldown"] = 500

        # Definir el rectángulo que activa el evento de fin de clase (se activa solo la primera vez)
        event_rect = pygame.Rect(470, 391, 162, 6)
        if (
            not globales_chapter_1.FIN_CLASE_EVENTO_ACTIVADO
            and self.player.rect.colliderect(event_rect)
        ):
            self.class_event_active = True
            globales_chapter_1.FIN_CLASE_EVENTO_ACTIVADO = True
            self.class_event_timer = 4000  # 4 segundos de evento de fin de clase
            self.classroom_sound.play()
            return None

        # Transición para regresar al pasillo segundo piso
        door_interior_to_edificio_h2 = pygame.Rect(509, 447, 100, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_h2):
            self.player.rect.center = (722, 280)
            return "interior_edificio_h2"

        return None

    def get_hud_visibility(self):
        # Si estamos en el evento de fin de clase, ocultamos el HUD
        if self.class_event_active:
            return False

        # Si estamos en el evento celular, ocultamos el HUD
        if self.cellphone_event_active:
            return False

        # Si hay alguna conversación activa con los NPCs, ocultamos el HUD.
        if any(state["conversation_active"] for state in self.npc_states.values()):
            return False

        return True

    def render(self):
        # Si el evento de fin de clase está activo, se muestra la pantalla en negro con "Fin de clase" y "9:00pm"
        if self.class_event_active:
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont("arial", 48, bold=True)
            text1 = font.render("Fin de clase", True, (255, 255, 255))
            text2 = font.render("9:00pm", True, (255, 255, 255))
            self.screen.blit(
                text1,
                (
                    (self.screen.get_width() - text1.get_width()) // 2,
                    self.screen.get_height() // 2 - 30,
                ),
            )
            self.screen.blit(
                text2,
                (
                    (self.screen.get_width() - text2.get_width()) // 2,
                    self.screen.get_height() // 2 + 30,
                ),
            )
            pygame.display.flip()
            return

        # Si el evento celular está activo, mostramos la imagen del celular y el diálogo de Alex
        if self.cellphone_event_active:
            self.screen.fill((0, 0, 0))
            try:
                cellphone_img = pygame.image.load(
                    "../assets/items/marian_mensaje.png"
                ).convert_alpha()
                # Escalar la imagen a un tamaño adecuado (por ejemplo, 200x200)
                cellphone_img = pygame.transform.scale(cellphone_img, (400, 700))
                globales_chapter_1.EMILIAN_VISIBLE = False
            except Exception as e:
                print("Error loading marian_mensaje asset:", e)
                cellphone_img = None

            if cellphone_img:
                img_x = (self.screen.get_width() - cellphone_img.get_width()) // 2
                img_y = (
                    self.screen.get_height() - cellphone_img.get_height()
                ) // 2 - 50

                self.screen.blit(cellphone_img, (img_x, img_y))
            # Mostrar el diálogo de Alex debajo de la imagen
            font = pygame.font.SysFont("arial", 24)
            dialogue_text = "Debo ir al edificio i para ver a mi tutora."
            rendered_text = font.render(dialogue_text, True, (255, 255, 255))
            text_x = (self.screen.get_width() - rendered_text.get_width()) // 2
            text_y = img_y + (cellphone_img.get_height() if cellphone_img else 0) + 10
            self.screen.blit(rendered_text, (text_x, text_y))
            pygame.display.flip()
            return

        # Renderizado normal de la escena del salón
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

        for npc in self.npcs:
            world_surface.blit(
                npc.image,
                (npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1]),
            )
        self.map.draw_primer_plano(world_surface, camera_offset)
        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        for npc in self.npcs:
            state = self.npc_states[npc]
            npc_screen_x = npc.rect.centerx - camera_offset[0]
            npc_screen_y = npc.rect.top - camera_offset[1]

            if not state["conversation_active"] and self.player.rect.colliderect(
                npc.rect
            ):
                draw_prompt(self.screen, (npc_screen_x, npc_screen_y - 20))

            if state["conversation_active"] and state["conversation_line_index"] < len(
                state["conversation_lines"]
            ):
                speaker, text = state["conversation_lines"][
                    state["conversation_line_index"]
                ]
                draw_dialogue(self.screen, speaker or npc.name, text)
