import pygame
import os
import csv
import json

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
                mouse_held_down = True
                selected_tile_id = place_tile(*event.pos, selected_tile_id)  # Update selected_tile_id
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
