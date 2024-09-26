import pygame
import os
import csv
import json


menu_data = {
    'menu_rect': pygame.Rect(0, 0, 100, 30),  # Position and size of the menu button
    'menu_text': "Tools",
    'dropdown_items': [
        {'name': "Add Layout Layer", 'action': 'add_layer'},
        # Add more tools here as needed
    ],
    'is_open': False  # To track if the dropdown is open
}



# Initialize Pygame
pygame.init()
font = pygame.font.SysFont(None, 24)  # This will select a default system font, with a size of 24

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

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT_WITH_PALETTE))
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()

# Load tile images (assuming they are in a folder named 'tiles')
tile_images = {}
tile_folder = 'tiles'
for tile_name in os.listdir(tile_folder):
    if tile_name.endswith('.png'):
        tile_id = tile_name.split('.')[0]
        image = pygame.image.load(os.path.join(tile_folder, tile_name)).convert_alpha()
        tile_images[tile_id] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))  # Resize the image
# Tile palette settings
TILES_PER_ROW = len(tile_images)  # You can adjust this based on the number of tiles and screen width
tile_palette_surface = pygame.Surface((SCREEN_WIDTH, PALETTE_AREA_HEIGHT))
tile_palette_rects = {}  # To store the rects for clickable areas in the palette

# Initialize the level data structure
level_data = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def add_layer():
    global level_data  # Reference the global variable
    layer_name = input("Enter new layer name: ")  # This is a placeholder; use a proper input method in Pygame
    new_layer = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    level_data.append({'name': layer_name, 'data': new_layer})




def draw_menu():
    # Draw the main menu button
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
        menu_data['is_open'] = not menu_data['is_open']  # Toggle menu open state
    elif menu_data['is_open']:
        for i, item in enumerate(menu_data['dropdown_items']):
            item_rect = pygame.Rect(menu_data['menu_rect'].left, menu_data['menu_rect'].bottom + i * 30, 100, 30)
            if item_rect.collidepoint(pos):
                menu_data['is_open'] = False  # Close the menu
                # Perform the action associated with the menu item
                if item['action'] == 'add_layer':
                    add_layer()  # You need to implement this function
                break





def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_palette():
    tile_palette_surface.fill(DARK_GRAY)
    x_offset = 0
    y_offset = 20  # Adjust based on palette layout
    for tile_id, tile_surface in tile_images.items():
        rect = tile_surface.get_rect(topleft=(x_offset, y_offset))
        tile_palette_surface.blit(tile_surface, rect)
        tile_palette_rects[tile_id] = rect.move(0, SCREEN_HEIGHT)  # Adjust rect positions for actual screen coordinates
        x_offset += TILE_SIZE
        if x_offset >= SCREEN_WIDTH:
            x_offset = 0
            y_offset += TILE_SIZE
    screen.blit(tile_palette_surface, (0, SCREEN_HEIGHT))



def place_tile(x, y, selected_tile_id):
    if y > SCREEN_HEIGHT:  # Check if click is in the palette area
        for tile_id, rect in tile_palette_rects.items():
            if rect.collidepoint((x, y)):
                return tile_id  # Return the new selected tile ID
    else:  # Click is in the grid area
        if selected_tile_id:
            grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
            level_data[grid_y][grid_x] = selected_tile_id
    return selected_tile_id  # Return the current selected tile ID if not updated

def run_editor():
    selected_tile_id = None
    running = True
    mouse_held_down = False  # Variable to track mouse button state


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Call handle_menu_click regardless of mouse_held_down state
                handle_menu_click(event.pos)  # Check if menu or dropdown item was clicked
                if not menu_data['is_open']:  # Only place tiles if the menu is not open
                    mouse_held_down = True
                    selected_tile_id = place_tile(*event.pos, selected_tile_id)
            elif event.type == pygame.MOUSEBUTTONUP:
               mouse_held_down = False

            if mouse_held_down:
                # Get the current mouse position and place a tile if the mouse is held down
                mouse_pos = pygame.mouse.get_pos()
                selected_tile_id = place_tile(*mouse_pos, selected_tile_id)  # Update selected_tile_id

        screen.fill(WHITE)
        draw_grid()
        draw_palette()

        # Draw placed tiles
        for y, row in enumerate(level_data):
            for x, tile_id in enumerate(row):
                if tile_id:
                    screen.blit(tile_images[tile_id], (x * TILE_SIZE, y * TILE_SIZE))

        draw_menu() 
        pygame.display.flip()
        clock.tick(60)

    save_level()



def save_level():
    # Save the level data to a CSV file
    with open('level.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(level_data)
    # Save the tile definitions to a JSON file
    with open('tiles.json', 'w') as jsonfile:
        json.dump(tile_images.keys(), jsonfile)

run_editor()
