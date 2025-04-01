import pygame
from map import Map
from collision_data import get_collisions
from scenes_chapter_2.scene import Scene
import globales_chapter_1
from scenes_chapter_2.salon_h2_scene import SalonH2Scene  
from scenes_chapter_2.interior_cafeteria import InteriorCafeteriaScene  
from scenes_chapter_2.interior_edificio_i2_scene import InteriorEdificioI2  

class InteriorEdificioI(Scene):
    def _init_(self, screen, player):
        super()._init_(screen)
        self.screen = screen
        self.map = Map("pasillo_i1.png")
        self.obstacles = get_collisions("hallway_i1")
        self.player = player
        self.player_group = pygame.sprite.Group(self.player)
        self.DEFAULT_ZOOM = 2
        self.current_map = "interior_edificio_i"
        
        # Inicializar la sombra y temporizador de parpadeo
        self.shadow_img = pygame.image.load("../assets/characters/fantasma_frente.png").convert_alpha()
        self.shadow_img = pygame.transform.scale(self.shadow_img, (20, 20))  # Ajusta el tamaño de la sombra
        self.shadow_rect = self.shadow_img.get_rect(topleft=(277, 218))
        self.shadow_visible = False
        self.shadow_timer = 0  # Temporizador para el parpadeo
        self.shadow_duration = 3000  # 3 segundos para el parpadeo
        self.shadow_blink_interval = 250  # Intervalo de parpadeo en milisegundos
        self.shadow_blink_time = 0  # Temporizador para controlar el parpadeo

        # Mensaje de emergencia cuando el pasillo se vuelve corrupto
        self.show_message = False
        self.message = "¿Qué es esto? ¡Lo mejor es ir a dormir!"
        self.message_timer = 0

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.player.update(dt, self.obstacles)
        self.player.clamp_within_map(self.map.fondo_rect)

        # Verificar si deben parpadear los 3 segundos de la sombra
        if self.shadow_timer > 0:
            self.shadow_timer -= dt
            if self.shadow_timer <= 0:
                # Desaparecer la sombra después de 3 segundos y volver al mapa normal
                self.shadow_visible = False
                self.map = Map("pasillo_i1.png")  # Restaurar el mapa original
                self.obstacles = get_collisions("hallway_i1")

        if self.shadow_visible:
            # Parpadeo de la sombra cada intervalo
            self.shadow_blink_time -= dt
            if self.shadow_blink_time <= 0:
                self.shadow_blink_time = self.shadow_blink_interval
                # Alternar visibilidad de la sombra
                self.shadow_visible = not self.shadow_visible

        # Transición para regresar a jardineras
        door_interior_to_jardineras = pygame.Rect(221, 496, 200, 5)
        if self.player.rect.colliderect(door_interior_to_jardineras):
            self.player.rect.center = (871, 392)
            return "jardineras_noche"

        # Transición para ir a segundo piso
        door_interior_to_edificio_h2 = pygame.Rect(303, 22, 93, 5)
        if self.player.rect.colliderect(door_interior_to_edificio_h2):
            self.player.rect.center = (336, 429)
            return "interior_edificio_i2"

        # Transición para entrar al baño izquierdo
        door_interior_to_banio_izquierdo = pygame.Rect(197, 109, 5, 47)
        if self.player.rect.colliderect(door_interior_to_banio_izquierdo):
            self.player.rect.center = (485, 265)
            return "banio_izquierdo_i"

        # Transición para entrar al baño derecho
        door_interior_to_banio_derecho = pygame.Rect(454, 109, 5, 47)
        if self.player.rect.colliderect(door_interior_to_banio_derecho):
            self.player.rect.center = (68, 280)
            return "banio_derecho_i"

        # Cambiar el mapa a pasillo_i1_corrupto si las 3 notas han sido tomadas
        if SalonH2Scene.note_taken_flag and InteriorCafeteriaScene.note_taken_flag and InteriorEdificioI2.note_taken_flag:
            self.map = Map("pasillo_i1_corrupto.jpeg")  # Cambiar a pasillo_i1_corrupto
            self.obstacles = get_collisions("hallway_i1")
            self.show_message = True
            self.message_timer = 3000  # Mostrar el mensaje por 3 segundos

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

        if self.shadow_visible:
            # Dibujar la sombra solo si es visible
            world_surface.blit(
                self.shadow_img,
                (self.shadow_rect.x - camera_offset[0], self.shadow_rect.y - camera_offset[1])
            )

        self.map.draw_primer_plano(world_surface, camera_offset)
        current_width, current_height = self.screen.get_size()
        scaled_surface = pygame.transform.scale(
            world_surface, (current_width, current_height)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Si el mensaje está activado, mostrarlo con más emoción
        if self.show_message:
            self.display_message(self.message)

    def display_message(self, message):
        # Mostrar el mensaje con más emoción en la parte inferior
        font = pygame.font.Font(None, 40)
        text_surface = font.render(message, True, (255, 0, 0))  # Usar un color rojo dramático
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 60))

        # Fondo del cuadro de diálogo
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.screen.get_height() - 100, self.screen.get_width(), 100))  # Fondo negro
        pygame.draw.rect(self.screen, (255, 255, 255), (0, self.screen.get_height() - 100, self.screen.get_width(), 100), 3)  # Borde blanco

        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # Reducir el tiempo de visualización del mensaje
        self.message_timer -= 100  # Disminuir el tiempo restante
        if self.message_timer <= 0:
            self.show_message = False

    def get_hud_visibility(self):
        # Si el mensaje está activado, ocultamos el HUD
        if self.show_message:
            return False
        return True