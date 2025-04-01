import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_dialogue(surface, name, text, face_expression=None):
    # Obtener el tamaño actual de la superficie (ventana)
    width, height = surface.get_size()

    # Definir el alto del recuadro de diálogo (por ejemplo, 25% de la altura de la ventana)
    dialogue_box_height = int(height * 0.25)

    # Crear el recuadro del diálogo con transparencia
    dialogue_box = pygame.Surface((width, dialogue_box_height))
    dialogue_box.set_alpha(200)
    dialogue_box.fill((0, 0, 0))
    # Dibujar el recuadro en la parte inferior de la pantalla
    surface.blit(dialogue_box, (0, height - dialogue_box_height))

    # Configuración para la imagen del rostro
    face_img = None
    face_padding = int(dialogue_box_height * 0.1)
    face_size = int(dialogue_box_height * 0.8)  # ancho y alto del cuadro de rostro
    if face_expression:
        face_path = f"assets/characters_dialog/{face_expression}.png"
        try:
            face_img = pygame.image.load(face_path).convert_alpha()
            face_img = pygame.transform.scale(face_img, (face_size, face_size))
        except Exception as e:
            print("Error al cargar la imagen de diálogo:", face_path, e)

    # Configurar fuentes (ajustadas en función del alto del diálogo)
    font_size_name = int(dialogue_box_height * 0.15)
    font_size_text = int(dialogue_box_height * 0.12)
    font_name = pygame.font.SysFont("arial", font_size_name, bold=True)
    font_text = pygame.font.SysFont("arial", font_size_text)

    # Posición horizontal inicial para el texto (deja espacio para la imagen si existe)
    x_offset = int(width * 0.05)
    if face_img:
        # Dibujar la imagen del rostro en el cuadro de diálogo, centrada verticalmente
        face_y = height - dialogue_box_height + face_padding
        surface.blit(face_img, (x_offset, face_y))
        x_offset += face_size + int(width * 0.02)  # espacio extra después de la imagen

    # Dibujar el nombre del personaje
    rendered_name = font_name.render(name, True, (255, 255, 0))
    name_y = height - dialogue_box_height + face_padding
    surface.blit(rendered_name, (x_offset, name_y))

    # Preparar el texto respetando los saltos de línea
    max_text_width = width - x_offset - int(width * 0.05)
    lines = []
    # Separamos por saltos de línea y luego procesamos cada párrafo
    for paragraph in text.splitlines():
        words = paragraph.split()
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font_text.size(test_line)[0] > max_text_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

    # Dibujar el texto debajo del nombre con un pequeño margen
    text_y = name_y + rendered_name.get_height() + int(dialogue_box_height * 0.05)
    for line in lines:
        rendered_line = font_text.render(line, True, (255, 255, 255))
        surface.blit(rendered_line, (x_offset, text_y))
        text_y += rendered_line.get_height() + int(dialogue_box_height * 0.02)


def draw_hotbar(
    surface,
    inventory,
    selected_slot,
    slot_count=4,
    slot_width=50,
    slot_height=50,
    padding=5,
):
    base_width, base_height = 800, 600
    current_width, current_height = surface.get_size()
    scale_x = current_width / base_width
    scale_y = current_height / base_height

    # Escalar dimensiones
    scaled_slot_width = int(slot_width * scale_x)
    scaled_slot_height = int(slot_height * scale_y)
    scaled_padding = int(padding * scale_x)

    total_width = slot_count * scaled_slot_width + (slot_count - 1) * scaled_padding
    start_x = (current_width - total_width) // 2
    y = current_height - scaled_slot_height - int(10 * scale_y)

    for i in range(slot_count):
        slot_rect = pygame.Rect(
            start_x + i * (scaled_slot_width + scaled_padding),
            y,
            scaled_slot_width,
            scaled_slot_height,
        )
        # Dibujar borde (más grueso si está seleccionado)
        border_width = int(3 * scale_x) if i == selected_slot else int(2 * scale_x)
        color = (255, 255, 0) if i == selected_slot else (255, 255, 255)
        pygame.draw.rect(surface, color, slot_rect, border_width)

        if i < len(inventory):
            # Ajustamos el tamaño del ítem con un margen
            item_margin = int(10 * scale_x)
            item_image = pygame.transform.scale(
                inventory[i].image,
                (scaled_slot_width - item_margin, scaled_slot_height - item_margin),
            )

            surface.blit(
                item_image,
                (slot_rect.x + int(5 * scale_x), slot_rect.y + int(5 * scale_y)),
            )


def draw_prompt(surface, pos):
    base_resolution = (800, 600)
    current_resolution = surface.get_size()
    scale_x = current_resolution[0] / base_resolution[0]
    scale_y = current_resolution[1] / base_resolution[1]
    scaled_pos = (int(pos[0] * scale_x), int(pos[1] * scale_y))
    font_size = max(10, int(18 * scale_y))
    font = pygame.font.SysFont("arial", font_size)
    # prompt_text = "Presiona E para interactuar"
    prompt_text = ""
    rendered_prompt = font.render(prompt_text, True, (255, 255, 0))
    prompt_rect = rendered_prompt.get_rect(center=scaled_pos)
    surface.blit(rendered_prompt, prompt_rect)


def draw_inventory(surface, item_image, text):
    base_resolution = (800, 600)
    current_width, current_height = surface.get_size()
    scale_x = current_width / base_resolution[0]
    scale_y = current_height / base_resolution[1]

    inv_box_width = int(100 * scale_x)
    inv_box_height = int(80 * scale_y)
    inv_box = pygame.Surface((inv_box_width, inv_box_height))
    inv_box.fill((50, 50, 50))
    surface.blit(inv_box, (int(10 * scale_x), current_height - int(90 * scale_y)))

    big_item = pygame.transform.scale(
        item_image, (int(70 * scale_x), int(70 * scale_y))
    )
    surface.blit(big_item, (int(15 * scale_x), current_height - int(85 * scale_y)))

    font = pygame.font.SysFont("arial", int(18 * scale_y))
    rendered_text = font.render(text, True, (255, 255, 255))
    surface.blit(rendered_text, (int(90 * scale_x), current_height - int(70 * scale_y)))


def draw_health_bar(surface, x, y, health, max_health):
    base_resolution = (800, 600)
    current_width, current_height = surface.get_size()
    scale_x = current_width / base_resolution[0]
    scale_y = current_height / base_resolution[1]

    bar_width = int(200 * scale_x)
    bar_height = int(20 * scale_y)
    fill_width = int((health / max_health) * bar_width)

    # Dibujar fondo (rojo)
    pygame.draw.rect(
        surface,
        (255, 0, 0),
        (int(x * scale_x), int(y * scale_y), bar_width, bar_height),
    )
    # Dibujar la parte de la salud actual (verde)
    pygame.draw.rect(
        surface,
        (0, 255, 0),
        (int(x * scale_x), int(y * scale_y), fill_width, bar_height),
    )
    # Dibujar borde
    pygame.draw.rect(
        surface,
        (255, 255, 255),
        (int(x * scale_x), int(y * scale_y), bar_width, bar_height),
        int(2 * scale_x),
    )
