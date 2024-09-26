import pygame
import os
import csv
import json
import shutil 

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = 25, 15  # Adjust based on your needs
SCREEN_WIDTH, SCREEN_HEIGHT = GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE
PALETTE_AREA_HEIGHT = 100  # Space at the bottom for the tile palette
SCREEN_HEIGHT_WITH_PALETTE = SCREEN_HEIGHT + PALETTE_AREA_HEIGHT

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Setup screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT_WITH_PALETTE))
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Load tile images from 'tiles' folder
tile_images = {}
tile_folder = 'tiles'
for tile_name in os.listdir(tile_folder):
    if tile_name.endswith('.png'):
        tile_id = tile_name.split('.')[0]
        image = pygame.image.load(os.path.join(tile_folder, tile_name)).convert_alpha()
        tile_images[tile_id] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

# Initialize level data with multiple layers
level_data = [{'name': 'Base Layer', 'data': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]}]
current_layer = 0  # Index of the current active layer

# Menu and dropdown items
menu_data = {
    'menu_rect': pygame.Rect(0, 0, 140, 30),
    'menu_text': "Tools",
    'dropdown_items': [
        {'name': "Add Layout Layer", 'action': 'add_layer'},
        {'name': "Switch Layer", 'action': 'switch_layer'},
        # Add more tools/actions as needed
    ],
    'is_open': False
}

def get_tile_id_to_constant_mapping(level_data):
    tile_ids = set(tile_id for layer in level_data for row in layer['data'] for tile_id in row if tile_id)
    return {tile_id: index + 1 for index, tile_id in enumerate(tile_ids)}


def add_layer():
    name_ = input("Enter layer name :  ")
    if name_ == '' :name_ = f"Layer {len(level_data)}"  # Automatically name layers
    new_layer = {'name': name_, 'data': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]}
    level_data.append(new_layer)
    print(f"Added new layer: {name_}")

def switch_layer():
    global current_layer
    current_layer = (current_layer + 1) % len(level_data)  # Cycle through layers
    print(f"Switched to layer: {level_data[current_layer]['name']}")

def draw_menu():
    pygame.draw.rect(screen, GRAY, menu_data['menu_rect'])
    menu_text_surface = font.render(menu_data['menu_text'], True, WHITE)
    screen.blit(menu_text_surface, menu_data['menu_rect'].topleft)

    if menu_data['is_open']:
        for i, item in enumerate(menu_data['dropdown_items']):
            item_rect = pygame.Rect(menu_data['menu_rect'].left, menu_data['menu_rect'].bottom + i * 30, 100, 30)
            pygame.draw.rect(screen, DARK_GRAY, item_rect)
            item_text_surface = font.render(item['name'], True, WHITE)
            screen.blit(item_text_surface, item_rect.topleft)

def handle_menu_click(pos):
    if menu_data['menu_rect'].collidepoint(pos):
        menu_data['is_open'] = not menu_data['is_open']
    elif menu_data['is_open']:
        for i, item in enumerate(menu_data['dropdown_items']):
            item_rect = pygame.Rect(menu_data['menu_rect'].left, menu_data['menu_rect'].bottom + i * 30, 100, 30)
            if item_rect.collidepoint(pos):
                menu_data['is_open'] = False  # Close the menu
                if item['action'] == 'add_layer':
                    add_layer()
                elif item['action'] == 'switch_layer':
                    switch_layer()
                break

def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_palette():
    tile_palette_surface = pygame.Surface((SCREEN_WIDTH, PALETTE_AREA_HEIGHT))
    tile_palette_surface.fill(DARK_GRAY)
    x_offset, y_offset = 0, 20
    tile_palette_rects = {}

    for tile_id, tile_surface in tile_images.items():
        rect = tile_surface.get_rect(topleft=(x_offset, y_offset))
        tile_palette_surface.blit(tile_surface, rect)
        tile_palette_rects[tile_id] = rect.move(0, SCREEN_HEIGHT)
        x_offset += TILE_SIZE
        if x_offset >= SCREEN_WIDTH:
            x_offset = 0
            y_offset += TILE_SIZE
    screen.blit(tile_palette_surface, (0, SCREEN_HEIGHT))
    return tile_palette_rects

def place_tile(x, y, selected_tile_id, tile_palette_rects, mouse_button):
    if y > SCREEN_HEIGHT:  # Click is in the palette area
        for tile_id, rect in tile_palette_rects.items():
            if rect.collidepoint((x, y)):
                return tile_id  # New selected tile ID
    else:  # Click is in the grid area
        grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
        if mouse_button == 1:  # Left-click to place tile
            if selected_tile_id:
                level_data[current_layer]['data'][grid_y][grid_x] = selected_tile_id
        elif mouse_button == 3:  # Right-click to delete tile
            level_data[current_layer]['data'][grid_y][grid_x] = None
    return selected_tile_id

def draw_tiles():
    # Get the current layer's data
    layer_data = level_data[current_layer]['data']
    for y, row in enumerate(layer_data):
        for x, tile_id in enumerate(row):
            if tile_id:
                screen.blit(tile_images[tile_id], (x * TILE_SIZE, y * TILE_SIZE))

def run_editor():
    selected_tile_id = None
    mouse_held_down = False
    editor_started = False  # Flag to indicate if the editing has started

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_level()
                return  # Exit the editor
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_menu_click(event.pos)
                # Start editing only after the first layer is added
                if editor_started:
                    if not menu_data['is_open']:  # Ignore clicks if the menu is open
                        mouse_held_down = True
                        selected_tile_id = place_tile(*event.pos, selected_tile_id, tile_palette_rects, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held_down = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_level()  # Save level when Ctrl+S is pressed

        if mouse_held_down and editor_started:
            # Update tiles as the mouse moves, if the button is held down
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_tile_id = place_tile(mouse_x, mouse_y, selected_tile_id, tile_palette_rects, pygame.mouse.get_pressed()[0])

        screen.fill(WHITE)
        draw_grid()
        draw_tiles()
        tile_palette_rects = draw_palette()
        draw_menu()

        pygame.display.flip()
        clock.tick(60)

        # Start editing once the first layer is added
        if len(level_data) > 0 and not editor_started:
            editor_started = True


def save_level():
    level_name = input("Enter level name: ")
    level_path = os.path.join('levels', level_name)

    # Create the main level directory
    os.makedirs(level_path, exist_ok=True)

    # Get tile ID to constant mapping
    tile_id_to_constant = get_tile_id_to_constant_mapping(level_data)

    # Iterate through each layer in the level data
    for layer_index, layer in enumerate(level_data):
        layer_name = layer['name']
        layer_path = os.path.join(level_path, layer_name)

        # Create a directory for the layer
        os.makedirs(layer_path, exist_ok=True)

        # Create a directory for tile images within the layer directory
        tile_images_path = os.path.join(layer_path, 'tile_images')
        os.makedirs(tile_images_path, exist_ok=True)

        # Copy used tile images into the tile_images directory
        for tile_id in tile_id_to_constant.keys():
            original_tile_path = os.path.join(tile_folder, f'{tile_id}.png')
            shutil.copy(original_tile_path, tile_images_path)

        # Generate layout JSON
        layout_json = {
            "layouts": [
                {
                    "name": layer_name,
                    "csv_layout_path": os.path.join(layer_path, f"{layer_name}_csv.csv"),
                    "tiles": [
                        {
                            "tile_image_path": os.path.join(tile_images_path, f"{tile_id}.png"),
                            "csv_constant_value": tile_id_to_constant[tile_id]
                        }
                        for tile_id in tile_id_to_constant.keys()
                    ]
                }
            ]
        }
        with open(os.path.join(layer_path, f'{layer_name}_layout.json'), 'w') as json_file:
            json.dump(layout_json, json_file, indent=4)

        # Generate and save CSV using the constant values
        with open(os.path.join(layer_path, f'{layer_name}_csv.csv'), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for row in layer['data']:
                writer.writerow([tile_id_to_constant.get(tile_id) for tile_id in row])

    print(f"Level '{level_name}' saved successfully.")


run_editor()
