import pygame
import random
from map import Map
from collision_data import get_collisions
from sound_manager import SoundManager
from scenes_chapter_1.scene import Scene
from npc import NPC
from utils import draw_dialogue, draw_prompt
import conversaciones_chapter1


class EntradaNocheScene(Scene):
    def __init__(self, screen, player):
        super().__init__(screen)
        # Suponemos que los assets para entrada_noche están en "entrada_noche.png" y "entrada_noche_objetos.png"
        self.map = Map("entrada_noche.png", "entrada_noche_obstaculos.png")
        self.obstacles = get_collisions("entrada")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.sound_manager = SoundManager()
        self.sound_manager.play_background("ambience.mp3", fade_in_ms=1000)
        self.sound_manager.set_volume(0.1)
        self.DEFAULT_ZOOM = 2
        self.current_map = "entrada_noche"

        # Crear múltiples NPCs
        self.npcs = [
            NPC(88, 824, "NPC_4.png", "Mariano", ""),
            NPC(476, 880, "NPC_5.png", "Gustavo", ""),
            NPC(834, 692, "NPC_6.png", "Manuel", ""),
            NPC(216, 352, "NPC_7.png", "Gurrola", ""),
            NPC(1440, 786, "NPC_8.png", "Joshua", ""),
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
        # Ejemplo de transición: si el jugador colisiona con la zona de salida hacia la calle
        door_entrada_to_calle = pygame.Rect(0, 960, 300, 10)
        if self.player.rect.colliderect(door_entrada_to_calle):
            # Reposicionar al jugador en la entrada de la calle; ajusta según convenga
            self.player.rect.center = (350, 60)
            return "calle"
        door_entrada_to_cafeteria = pygame.Rect(1490, 0, 10, 1000)
        if self.player.rect.colliderect(door_entrada_to_cafeteria):
            self.player.rect.center = (150, 860)
            return "cafeteria_noche"
        return None

    def get_hud_visibility(self):
        # Si hay alguna conversación activa con los NPCs, ocultamos el HUD.
        if any(state["conversation_active"] for state in self.npc_states.values()):
            return False

        # Si no hay conversaciones activas, mostramos el HUD.
        return True

    def render(self):
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
        view_width = VIRTUAL_WIDTH / self.DEFAULT_ZOOM
        view_height = VIRTUAL_HEIGHT / self.DEFAULT_ZOOM
        camera_offset_x = max(
            0,
            min(
                self.player.rect.centerx - view_width / 2,
                self.map.fondo_rect.width - view_width,
            ),
        )
        camera_offset_y = max(
            0,
            min(
                self.player.rect.centery - view_height / 2,
                self.map.fondo_rect.height - view_height,
            ),
        )
        camera_offset = (camera_offset_x, camera_offset_y)

        world_surface = pygame.Surface((int(view_width), int(view_height)))
        world_surface.fill((0, 0, 0))
        self.map.draw_fondo(world_surface, camera_offset)

        world_surface.blit(
            self.player.image,
            (
                self.player.rect.x - camera_offset[0],
                self.player.rect.y - camera_offset[1],
            ),
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
