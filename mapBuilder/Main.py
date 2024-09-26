import pygame
import os
import csv
import json
import shutil 

# Initialize Pygame
pygame.init()

drawing_size = 1  # Default drawing size (1x1)
last_mouse_button = None

with open("enemy_mapping.json", "r") as file:
    enemy_mapping = json.load(file)

# Constants for palettes and tool area (Defined globally)
PALETTE_AREA_HEIGHT = 100  # Space at the bottom for the tile palette
OBJECT_AREA_HEIGHT = 100
ENEMY_AREA_HEIGHT = 100
TOOL_AREA_WIDTH = 150  # Width of the tool area


# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

BLUE = (100,20,40)
BLUE2 = (10,150,4)


# Define brush colors and transparency
OBSTRUCTION_BRUSH_COLOR = (0, 0, 255, 127)  # Blue with 50% transparency
TRIGGER_BRUSH_COLOR = (255, 0, 255, 127)  # Purple with 50% transparency

# Initialize the brush surfaces as None globally
obstruction_brush_surface = None
trigger_brush_surface = None
# Load tile images from 'tiles' folder
#tile_images = {}
tile_folder = 'tiles'
current_layer = 0  # Index of the current active layer
menu_data = None
# Load object images
#object_images = {}
object_folder = 'objects'  # Your object images folder
# Load Enemy objects
#enemy_images = {}
enemy_folder = 'enemies'  # Your enemies images folder

PALETTE_IMAGE_SIZE = 40  # Size of images in the palette

def load_and_scale_images(GRID_IMAGE_SIZE):
    global palette_tile_images, grid_tile_images, palette_object_images, grid_object_images, palette_enemy_images, grid_enemy_images


    

    tile_folder = 'tiles'
    object_folder = 'objects'
    enemy_folder = 'enemies'

    # Initialize dictionaries
    palette_tile_images = {}
    grid_tile_images = {}
    palette_object_images = {}
    grid_object_images = {}
    palette_enemy_images = {}
    grid_enemy_images = {}

    # Load and scale tile images
    for tile_name in os.listdir(tile_folder):
        if tile_name.endswith('.png'):
            tile_id = tile_name.split('.')[0]
            image = pygame.image.load(os.path.join(tile_folder, tile_name)).convert_alpha()
            palette_tile_images[tile_id] = pygame.transform.scale(image, (PALETTE_IMAGE_SIZE, PALETTE_IMAGE_SIZE))
            grid_tile_images[tile_id] = pygame.transform.scale(image, (GRID_IMAGE_SIZE, GRID_IMAGE_SIZE))

    # Repeat for objects and enemies
    for object_name in os.listdir(object_folder):
        if object_name.endswith('.png'):
            object_id = object_name.split('.')[0]
            image = pygame.image.load(os.path.join(object_folder, object_name)).convert_alpha()
            palette_object_images[object_id] = pygame.transform.scale(image, (PALETTE_IMAGE_SIZE, PALETTE_IMAGE_SIZE))
            grid_object_images[object_id] = pygame.transform.scale(image, (GRID_IMAGE_SIZE, GRID_IMAGE_SIZE))

    for enemy_name in os.listdir(enemy_folder):
        if enemy_name.endswith('.png'):
            enemy_id = enemy_name.split('.')[0]
            image = pygame.image.load(os.path.join(enemy_folder, enemy_name)).convert_alpha()
            palette_enemy_images[enemy_id] = pygame.transform.scale(image, (PALETTE_IMAGE_SIZE, PALETTE_IMAGE_SIZE))
            grid_enemy_images[enemy_id] = pygame.transform.scale(image, (GRID_IMAGE_SIZE, GRID_IMAGE_SIZE))



def initialize_game():
    global screen, GRID_WIDTH, GRID_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_HEIGHT_WITH_PALETTE, level_data, TOOL_AREA_WIDTH,menu_data,obstruction_brush_surface, trigger_brush_surface, PALETTE_IMAGE_SIZE

    # Constants for palettes and tool area
    PALETTE_AREA_HEIGHT = 100  # Space at the bottom for the tile palette
    OBJECT_AREA_HEIGHT = 100
    ENEMY_AREA_HEIGHT = 100
    TOOL_AREA_WIDTH = 150  # Width of the tool area

    # Prompt for grid dimensions and tile size
    GRID_WIDTH = int(input("Enter grid width (in tiles): "))
    GRID_HEIGHT = int(input("Enter grid height (in tiles): "))
    TILE_SIZE = int(input("Enter tile size (in pixels): "))



    # Calculate screen dimensions based on user input and constants
    SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE + TOOL_AREA_WIDTH  # Total width includes tool area
    SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE  # Height for the grid area only
    SCREEN_HEIGHT_WITH_PALETTE = SCREEN_HEIGHT + PALETTE_AREA_HEIGHT + OBJECT_AREA_HEIGHT + ENEMY_AREA_HEIGHT  # Total height includes palettes


    # Initialize menu_data with the correct position within the tool area
    PALETTE_IMAGE_SIZE = 40  # Size of images in the palette

    # Define brush colors and transparency
    OBSTRUCTION_BRUSH_COLOR = (0, 0, 255, 127)  # Blue with 50% transparency
    TRIGGER_BRUSH_COLOR = (255, 0, 255, 127)  # Purple with 50% transparency

    # Create surfaces for brushes
    obstruction_brush_surface = pygame.Surface((PALETTE_IMAGE_SIZE, PALETTE_IMAGE_SIZE), pygame.SRCALPHA)
    obstruction_brush_surface.fill(OBSTRUCTION_BRUSH_COLOR)

    trigger_brush_surface = pygame.Surface((PALETTE_IMAGE_SIZE, PALETTE_IMAGE_SIZE), pygame.SRCALPHA)
    trigger_brush_surface.fill(TRIGGER_BRUSH_COLOR)


    # Calculate the position for the menu within the tool area
    button_height = 30
    margin = 10
    number_of_buttons = 3
    additional_margin_before_menu = 20  # Extra space before the menu

    # Total vertical space occupied by existing buttons and margins
    occupied_space = (button_height + margin) * number_of_buttons + additional_margin_before_menu

    # Initialize menu_data with the correct position within the tool area
    menu_y_position = occupied_space  # This is the 'some_additional_offset' calculated
    menu_data = {
        'menu_rect': pygame.Rect(SCREEN_WIDTH - TOOL_AREA_WIDTH + 10, menu_y_position, 140, 30),
        'menu_text': "Tools",
        'dropdown_items': [
            {'name': "Add Layout Layer", 'action': 'add_layer'},
            {'name': "Switch Layer", 'action': 'switch_layer'},
            {'name': "Save", 'action': 'save'},
              
        ],
        'is_open': False
    }


    # Initialize or update level_data based on the new grid size
    level_data = [{
        'name': 'start',
        'tiles': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)],
        'objects': [],
        'enemies': []
    }]

    # Initialize the Pygame screen with the calculated dimensions
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT_WITH_PALETTE))
    pygame.display.set_caption("Level Editor")

    # Set up the clock and font for later use
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    load_and_scale_images(TILE_SIZE)

    # Return necessary variables that might be used outside this function
    return screen, clock, font, level_data



def draw_object_palette():

    
    object_palette_surface = pygame.Surface((SCREEN_WIDTH, OBJECT_AREA_HEIGHT))
    object_palette_surface.fill(BLUE)
    x_offset, y_offset = 0, 0  # Start at the beginning of the object palette
    object_palette_rects = {}

    for object_id, object_surface in palette_object_images.items():
        rect = object_surface.get_rect(topleft=(x_offset, y_offset))
        object_palette_surface.blit(object_surface, rect)
        # Move the rectangle's position to where it should be on the main screen, just below the tile palette
        object_palette_rects[object_id] = rect.move(0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT)
        x_offset += PALETTE_IMAGE_SIZE
        if x_offset >= SCREEN_WIDTH:
            x_offset = 0
            y_offset += PALETTE_IMAGE_SIZE

    # Add obstruction brush to the palette
    obstruction_brush_rect = obstruction_brush_surface.get_rect(topleft=(x_offset, y_offset))
    object_palette_surface.blit(obstruction_brush_surface, obstruction_brush_rect)
    object_palette_rects['obstruction_brush'] = obstruction_brush_rect.move(0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT)
    x_offset += PALETTE_IMAGE_SIZE

    # Add trigger brush to the palette
    trigger_brush_rect = trigger_brush_surface.get_rect(topleft=(x_offset, y_offset))
    object_palette_surface.blit(trigger_brush_surface, trigger_brush_rect)
    object_palette_rects['trigger_brush'] = trigger_brush_rect.move(0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT)
    x_offset += PALETTE_IMAGE_SIZE


    # Blit the object palette surface just below the tile palette
    screen.blit(object_palette_surface, (0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT))
    return object_palette_rects

def draw_enemy_palette():
    enemy_palette_surface = pygame.Surface((SCREEN_WIDTH, ENEMY_AREA_HEIGHT))
    enemy_palette_surface.fill(BLUE2)  # Set to your preferred color
    x_offset, y_offset = 0, 0  # Start drawing from the top-left corner of the enemy palette
    enemy_palette_rects = {}

    for enemy_id, enemy_surface in palette_enemy_images.items():
        rect = enemy_surface.get_rect(topleft=(x_offset, y_offset))
        enemy_palette_surface.blit(enemy_surface, rect)
        # Adjust the rect's position for it to appear just below the object palette area
        enemy_palette_rects[enemy_id] = rect.move(0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT + OBJECT_AREA_HEIGHT)
        x_offset += PALETTE_IMAGE_SIZE
        if x_offset >= SCREEN_WIDTH:
            x_offset = 0  # Reset x_offset to start a new row
            y_offset += PALETTE_IMAGE_SIZE  # Move down a row

    # Blit the enemy palette surface just below the object palette
    screen.blit(enemy_palette_surface, (0, SCREEN_HEIGHT + PALETTE_AREA_HEIGHT + OBJECT_AREA_HEIGHT))
    return enemy_palette_rects


def get_tile_id_to_constant_mapping(level_data):
    tile_ids = set(tile_id for layer in level_data for row in layer['tiles'] for tile_id in row if tile_id)
    return {tile_id: index + 1 for index, tile_id in enumerate(tile_ids)}


def add_layer():
    name_ = input("Enter layer name: ")
    if name_ == '':
        name_ = f"Layer {len(level_data)}"  # Automatically name layers
    new_layer = {
        'name': name_,
        'tiles': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)],
        'objects': [],
        'enemies': []  # Ensure this line is present
    }
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
                elif item['action'] == 'save':
                    save_level()
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

    for tile_id, tile_surface in palette_tile_images.items():
        rect = tile_surface.get_rect(topleft=(x_offset, y_offset))
        tile_palette_surface.blit(tile_surface, rect)
        tile_palette_rects[tile_id] = rect.move(0, SCREEN_HEIGHT)
        x_offset += PALETTE_IMAGE_SIZE
        if x_offset >= SCREEN_WIDTH:
            x_offset = 0
            y_offset += PALETTE_IMAGE_SIZE
    screen.blit(tile_palette_surface, (0, SCREEN_HEIGHT))
    return tile_palette_rects

def place_tile(x, y, selected_tile_id, tile_palette_rects,enemy_palette_rects, mouse_button, mouse_held_down):
    global last_mouse_button
    if mouse_held_down:
        # Use the last mouse button action stored when dragging
        mouse_button = last_mouse_button
        
    #print(f"CALL place_tile called with x: {x}, y: {y}, selected_tile_id: {selected_tile_id}, mouse_button: {mouse_button}, mouse_held_down: {mouse_held_down}")

    if y > SCREEN_HEIGHT:  # Click is in the palette area
        for tile_id, rect in tile_palette_rects.items():
            if rect.collidepoint((x, y)):
                return tile_id  # New selected tile ID
        

    if y > SCREEN_HEIGHT:  # Click is in the palette area
        for enemy_id, rect in enemy_palette_rects.items():
            if rect.collidepoint((x, y)):
                return tile_id  # New selected tile ID




    else:  # Click is in the grid area
        grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
        #print("mouse_button")    
        print(mouse_button)

          #if the mouse is held down, we need the mouse button to be the previously logged mouse button.
        # Loop through the tiles in the drawing area
        for dx in range(drawing_size):
            for dy in range(drawing_size):
                # Calculate the tile position
                tile_x = grid_x + dx
                tile_y = grid_y + dy

                # Check if the tile position is within the grid bounds
                if 0 <= tile_x < GRID_WIDTH and 0 <= tile_y < GRID_HEIGHT:
                    if mouse_button == 1:  # Left-click to place tile
                        # Place the tile if the tile position is valid and different from the current tile (to avoid unnecessary overwrites)
                        if selected_tile_id and (not mouse_held_down or (mouse_held_down and level_data[current_layer]['tiles'][tile_y][tile_x] != selected_tile_id)):
                            level_data[current_layer]['tiles'][tile_y][tile_x] = selected_tile_id
                    elif mouse_button == 3:  # Right-click to delete tile
                        # Delete the tile if the tile position is valid and not already empty
                        if not mouse_held_down or (mouse_held_down and level_data[current_layer]['tiles'][tile_y][tile_x] is not None):
                            level_data[current_layer]['tiles'][tile_y][tile_x] = None

    return selected_tile_id


def draw_tool_area():	
    global drawing_size
    # Draw the background for the tool area
    tool_area_rect = pygame.Rect(SCREEN_WIDTH - TOOL_AREA_WIDTH, 0, TOOL_AREA_WIDTH, SCREEN_HEIGHT_WITH_PALETTE)
    pygame.draw.rect(screen, DARK_GRAY, tool_area_rect)

    # Start drawing tool icons/buttons starting from the top of the tool area
    y_offset = 10  # Start 10 pixels from the top of the tool area

    # Drawing Size Selection
    text_surface = font.render('Drawing Size:', True, WHITE)
    screen.blit(text_surface, (SCREEN_WIDTH - TOOL_AREA_WIDTH + 10, y_offset))
    y_offset += text_surface.get_height() + 5  # Adjust y_offset for the next tool

    sizes = [1, 2, 3]  # Available drawing sizes
    for size in sizes:
        rect = pygame.Rect(SCREEN_WIDTH - TOOL_AREA_WIDTH + 10, y_offset, 30, 30)  # Rectangle for the size option
        pygame.draw.rect(screen, GRAY, rect, 1)  # Draw the rectangle
        text_surface = font.render(str(size), True, WHITE)
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            drawing_size = size  # Update the drawing size when clicked

        y_offset += rect.height + 10  # Adjust y_offset for the next tool, with 10 pixels gap

    # Add more tools/icons/buttons below this as needed


def place_enemy(x, y, selected_enemy_id, enemy_palette_rects, mouse_button):
    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
    if mouse_button == 1 and selected_enemy_id:  # Left-click to place enemy
        level_data[current_layer]['enemies'].append({
            'id': selected_enemy_id,
            'position': (grid_x, grid_y)
        })
        print(f"Placed enemy '{selected_enemy_id}' at grid position ({grid_x}, {grid_y})")
    elif mouse_button == 3:  # Right-click to remove enemy
        for enemy in level_data[current_layer]['enemies'][:]:
            if enemy['position'] == (grid_x, grid_y):
                level_data[current_layer]['enemies'].remove(enemy)
                print(f"Removed enemy at grid position ({grid_x}, {grid_y})")
                break


def place_object(points, selected_object_id):

    if not selected_object_id or len(points) != 4:
        print("Error: Invalid selection")
        return

    # Calculate the bounding box for the points to define the rectangle
    min_x = min(points, key=lambda x: x[0])[0] // TILE_SIZE
    max_x = max(points, key=lambda x: x[0])[0] // TILE_SIZE
    min_y = min(points, key=lambda x: x[1])[1] // TILE_SIZE
    max_y = max(points, key=lambda x: x[1])[1] // TILE_SIZE

    width = max_x - min_x +1
    height = max_y - min_y  +1

    # Initialize obstruction_matrix with all 1s (indicating full obstruction)
    # This matrix might be modified later using special brushes
    obstruction_matrix = [[1 for _ in range(width)] for _ in range(height)]

    # Initialize trigger_info with None or appropriate structure
    # This might be modified later based on specific trigger areas defined using a special brush
    trigger_matrix = [[0 for _ in range(width)] for _ in range(height)]


    object_data = {
        "id": selected_object_id,
        "image_path": os.path.join(object_folder, f"{selected_object_id}.png"),
        "object_info": {
            "width": width,
            "height": height,
            "x_pos": min_x,
            "y_pos": min_y,
            "obstruction_matrix": obstruction_matrix,
            "trigger_info":{ 
                "destination_layout_path" :"./",                
                "new_player_position":[4,4],
                "trigger_matrix":trigger_matrix
                          } 
       }
    }

    level_data[current_layer]['objects'].append(object_data)
    print(f"Appended object : {object_data}")
    


def draw_tiles(level_data, current_layer, selected_object_id, object_palette_rects):
    layer_data = level_data[current_layer]['tiles']
    #print(layer_data)
    for y, row in enumerate(layer_data):
        for x, tile_id in enumerate(row):
            if tile_id in grid_tile_images:
                #scaled_tile_image = pygame.transform.scale(tile_images[tile_id], (TILE_SIZE, TILE_SIZE))            
                tile_image = grid_tile_images[tile_id] 
                screen.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))
    

    # Draw enemies
    for enemy in level_data[current_layer]['enemies']:
        enemy_id = enemy['id']
        grid_x, grid_y = enemy['position']
        if enemy_id in grid_enemy_images:
            enemy_image = grid_enemy_images[enemy_id]
            screen.blit(enemy_image, (grid_x * TILE_SIZE, grid_y * TILE_SIZE))

       # Draw objects   
    
       # Draw objects with updated data structure
    for obj in level_data[current_layer]['objects']:
        object_info = obj['object_info']  # Access the nested 'object_info' dictionary
        x_pos, y_pos = object_info['x_pos'], object_info['y_pos']
        width, height = object_info['width'], object_info['height']

        # Calculate the scaled size based on TILE_SIZE
        scaled_width, scaled_height = width * TILE_SIZE, height * TILE_SIZE
#        print(obj['id'])
#        print(grid_object_images)
#        print(f"width:{width},height:{height}, xpos:{x_pos}, ypos:{y_pos}")
        object_image_id = grid_object_images[obj['id']]  # Assume 'id' is still directly under obj
        scaled_image = pygame.transform.scale(object_image_id, (scaled_width, scaled_height))
        screen.blit(scaled_image, (x_pos * TILE_SIZE, y_pos * TILE_SIZE))
                    
        # Draw special tiles for trigger and obstruction
        #trigger_tile_surface = object_palette_rects['trigger_brush'] 
       
#        print( object_info['obstruction_matrix'] )
        scaled_obstruction_surface = pygame.transform.scale(obstruction_brush_surface, (TILE_SIZE, TILE_SIZE))
        scaled_trigger_surface = pygame.transform.scale(trigger_brush_surface, (TILE_SIZE, TILE_SIZE))
        trigger_matrix = object_info['trigger_info']['trigger_matrix']
        for row_index, row in enumerate(trigger_matrix):
            for col_index, cell in enumerate(row):
                if cell == 1:  # There's a trigger in this cell
                    screen.blit(scaled_trigger_surface, ((x_pos + col_index) * TILE_SIZE, (y_pos + row_index) * TILE_SIZE))
        #obstruction_tile_surface = object_palette_rects['obstruction_brush']
        for row_index, row in enumerate(object_info['obstruction_matrix']):
            for col_index, cell in enumerate(row):
                if cell == 1:  # There's an obstruction in this cell
                    screen.blit(scaled_obstruction_surface, ((x_pos + col_index) * TILE_SIZE, (y_pos + row_index) * TILE_SIZE))

def is_rectangle(points):
    if len(points) != 4:
        return False

    # Calculate the vectors for the sides of the polygon
    vectors = []
    for i, point1 in enumerate(points):
        point2 = points[(i + 1) % 4]  # Get the next point in the list
        vectors.append((point2[0] - point1[0], point2[1] - point1[1]))

    # Calculate the dot product between each pair of vectors to find the angles
    for i, vector1 in enumerate(vectors):
        vector2 = vectors[(i + 1) % 4]  # Get the next vector in the list
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        if dot_product != 0:  # If the dot product is not 0, the angle is not 90 degrees
            return False

    return True


def distance(p1, p2):

    """Calculate the Euclidean distance between two points."""

    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

def is_rectangle_OLD(points):
    #print(points)
    if len(points) != 4:
        return False

    distances = []
    for i, point1 in enumerate(points):
        for j, point2 in enumerate(points):
            if i != j:
                distances.append(distance(point1, point2))
    #print(distances)
    unique_distances = set(distances)
    #print(unique_distances)
    if len(unique_distances) != 2:
        return False
    
    # Count the occurrences of each distance, expecting two sides to be equal and the other two sides also to be equal.
    if distances.count(min(unique_distances)) != 4 or distances.count(max(unique_distances)) != 4:
        return False

    return True


SPECIAL_BRUSHES = {'obstruction_brush', 'trigger_brush'}


highlighted_rects = [] 
def run_editor():

    global highlighted_rects,mouse_held_down,last_mouse_button
    selected_tile_id = None
    selected_object_id = None
    selected_enemy_id = None
    mouse_held_down = False
    editor_started = False
    #selection_start = None
    #selection_end = None
    points = []  # To store the selected points
    clicks_remaining = 4  # Counter for remaining clicks

    tile_palette_rects = draw_palette()  # Ensure this function is called to get tile palette rects
    object_palette_rects = draw_object_palette()  # Draw the object palette and get rects
    enemy_palette_rects = draw_enemy_palette()

    while True:
        for event in pygame.event.get():
            #print(f"Event: {event}")  # Log every event

            if event.type == pygame.QUIT:
                print("Quitting...")
                #save_level()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                last_mouse_button = event.button
                pos_x, pos_y = event.pos
                #print(f"Mouse down at: {event.pos}")
                handle_menu_click((pos_x, pos_y))
                # Check if the click is within the tile palette area
                if SCREEN_HEIGHT <= pos_y < SCREEN_HEIGHT + PALETTE_AREA_HEIGHT:
                   # print("In tile palette area")
                    for tile_id, rect in tile_palette_rects.items():
                        #print(rect.collidepoint((pos_x, pos_y )))
                        #print(f"{rect.x}_{rect.y}_{rect.width}_{rect.height}")
                        #print(pos_x)
                        #print(pos_y)
                        #print(rect) 
                        if rect.collidepoint((pos_x, pos_y)):
                            #print(f"Selected tile: {tile_id}")
                            selected_tile_id = tile_id
                            selected_object_id = None
                            selected_enemy_id = None
                            break

                # Check if the click is within the object palette area
                elif pos_y >= SCREEN_HEIGHT + PALETTE_AREA_HEIGHT and pos_y < SCREEN_HEIGHT + PALETTE_AREA_HEIGHT + OBJECT_AREA_HEIGHT :
                    print("In object palette area")
                    for object_id, rect in object_palette_rects.items():
                        if rect.collidepoint((pos_x, pos_y )):
                            #print(f"Selected object: {object_id}")
                            selected_object_id = object_id
                            selected_tile_id = None
                            selected_enemy_id = None
                            break

                elif pos_y >= SCREEN_HEIGHT + PALETTE_AREA_HEIGHT + OBJECT_AREA_HEIGHT:  # Enemy palette area
                    print("in enemy palette area")
                    for enemy_id, rect in enemy_palette_rects.items():
                        if rect.collidepoint((pos_x, pos_y)):
                           selected_enemy_id = enemy_id  # Select the enemy
                           selected_tile_id = None
                           selected_object_id = None
                           break

                # Clicks within the grid area
                elif pos_y < SCREEN_HEIGHT:
                    print("In grid area")
                    if selected_tile_id is not None:
                        mouse_held_down = True
                        print("Mouse hekd down")
                        print(mouse_held_down)

                        place_tile(pos_x, pos_y, selected_tile_id, tile_palette_rects,enemy_palette_rects,event.button,mouse_held_down)
                    
                    elif selected_enemy_id is not None:
                        mouse_held_down = True
                        print("mouse held down" ) 
                   
                        place_enemy( pos_x,pos_y, selected_enemy_id, enemy_palette_rects, event.button )
                                                
                    elif selected_object_id is not None:
                        if selected_object_id not in SPECIAL_BRUSHES:
                            print("Starting object placement")
                        
                            if clicks_remaining > 0:
                        
                                # Snap the click position to the grid
                                grid_x, grid_y = pos_x // TILE_SIZE * TILE_SIZE, pos_y // TILE_SIZE * TILE_SIZE

                                points.append((grid_x, grid_y))
                                clicks_remaining -= 1
                                # Draw red box at clicked point
                                #print("drawing red box in theory ")
    

                        
                       
                                highlighted_rects.append(((grid_x, grid_y), (TILE_SIZE, TILE_SIZE)))
                
                                if clicks_remaining == 0:
                                    if is_rectangle(points):
                                        # Proceed to object placement
                                        #print("Valid rectangle")



                                        # DRAW OBJECT !
                                        place_object( points, selected_object_id   )


                                            # Reset for next selectio  
                                        points = []
                                        clicks_remaining = 4
                                    else:
                                        # Display error and clear selection
                                        print("Invalid rectangle, please select again")
                                        points = []
                                        highlighted_rects = []
                                        clicks_remaining = 4    
                        if selected_object_id in SPECIAL_BRUSHES:
    
                                
                                handle_special_object_brush( selected_object_id )   

            elif event.type == pygame.MOUSEBUTTONUP:
                #print(f"Mouse up at: {event.pos}")
                mouse_held_down = False




            elif event.type == pygame.MOUSEMOTION and mouse_held_down and selected_tile_id:
                print(f"MOUSEMOTION with mouse_held_down: {mouse_held_down}, selected_tile_id: {selected_tile_id}")
                place_tile(event.pos[0], event.pos[1], selected_tile_id,tile_palette_rects,enemy_palette_rects, event.buttons, mouse_held_down)


        
        screen.fill(WHITE)
        for rect_pos, rect_size in highlighted_rects:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(rect_pos, rect_size), 2)
        
        
        draw_grid()
        draw_tiles(level_data, current_layer, selected_object_id, object_palette_rects)
        tile_palette_rects = draw_palette()
        object_palette_rects = draw_object_palette()
        enemy_palette_rects = draw_enemy_palette()
        
        draw_tool_area()
        draw_menu()
        pygame.display.flip()
        clock.tick(60)

        if len(level_data) > 0 and not editor_started:
            print("Editor started")
            editor_started = True


def handle_special_object_brush(selected_object_id):
    global level_data, current_layer
    
    print('IN SPECIAL BRUSH HANDLE ')
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Ensure the click is within the grid area
    if mouse_y < SCREEN_HEIGHT:
        grid_x, grid_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE

        # Find the object that the brush is being applied to
        for obj in level_data[current_layer]['objects']:
            object_info = obj['object_info']
            x_pos, y_pos = object_info['x_pos'], object_info['y_pos']
            width, height = object_info['width'], object_info['height']

            # Check if the brush is within the bounds of the object
            print(f"grid points {grid_x,grid_y}")
            print(f"object position : {x_pos},{y_pos},height:{height}, widht: {width}"  )
            if x_pos <= grid_x < x_pos + width and y_pos <= grid_y < y_pos + height:
                matrix_x, matrix_y = grid_x - x_pos, grid_y - y_pos  # Convert grid coordinates to matrix coordinates
                print("OBJECT IDENTIFIED")
                
                print(object_info['trigger_info'])
                print(f"selected_object_id: {selected_object_id}")
                # Update the appropriate matrix based on the brush type
                if selected_object_id == 'trigger_brush':

                    print( object_info['trigger_info'][matrix_y][matrix_x] )
                    object_info['trigger_info']['trigger_matrix'][matrix_y][matrix_x] ^= 1  # Set trigger at the matrix position
                    print( object_info['trigger_info'][matrix_y][matrix_x] )

                elif selected_object_id == 'obstruction_brush':
                    print( object_info['obstruction_matrix'][matrix_y][matrix_x] )
                    object_info['obstruction_matrix'][matrix_y][matrix_x] ^= 1  # Set obstruction at the matrix position
                    print( object_info['obstruction_matrix'][matrix_y][matrix_x] )



def save_level():
    level_name = input("Enter level name: ")
    level_path = os.path.join('../levels', level_name)

    # Create the main level directory
    os.makedirs(level_path, exist_ok=True)

    # Get tile ID to constant mapping
    tile_id_to_constant = get_tile_id_to_constant_mapping(level_data)

    # Initialize the set for used object IDs
    used_object_ids = set()

    # Iterate through each layer in the level data
    for layer_index, layer in enumerate(level_data):
        layer_name = layer['name']
        layer_path = os.path.join(level_path, layer_name)

        # Create a directory for the layer
        os.makedirs(layer_path, exist_ok=True)

        # Create a directory for tile images within the layer directory
        tile_images_path = os.path.join(layer_path, 'tile_images')
        os.makedirs(tile_images_path, exist_ok=True)

        # Create a directory for object images within the layer directory
        object_images_path = os.path.join(layer_path, 'Objects/object_images')
        os.makedirs(object_images_path, exist_ok=True)

        # Copy used tile images into the tile_images directory
        for tile_id in tile_id_to_constant.keys():
            original_tile_path = os.path.join(tile_folder, f'{tile_id}.png')
            shutil.copy(original_tile_path, tile_images_path)

        # Add object IDs from this layer to the set of used object IDs
        for obj in layer['objects']:
            used_object_ids.add(obj['id'])

    # Copy used object images into the object_images directory
        for object_id in used_object_ids:
            original_object_path = os.path.join(object_folder, f'{object_id}.png')
            shutil.copy(original_object_path, object_images_path)


        # Saving object data
        object_data_path = os.path.join(layer_path, "Objects/object_info.json")
        with open(object_data_path, 'w') as f:
            json.dump(layer['objects'], f, indent=4)



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
        with open(os.path.join(layer_path, f'{layer_name}_layout_definition.json'), 'w') as json_file:
            json.dump(layout_json, json_file, indent=4)

        # Generate and save CSV using the constant values
        with open(os.path.join(layer_path, f'{layer_name}_csv.csv'), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            print(layer)
            for row in layer['tiles']:
                writer.writerow([tile_id_to_constant.get(tile_id) for tile_id in row])

        # New code to handle enemies
        if 'enemies' in layer and layer['enemies']:
            enemy_layer_path = os.path.join(layer_path, 'Enemies')
            os.makedirs(enemy_layer_path, exist_ok=True)
            enemies_info = []
            print(layer['enemies'])
            for enemy_map_definition in layer['enemies']:
               
                # Assume `enemy_mapping` is your dictionary mapping enemy IDs to full enemy info
                print(f"Enemy map definition : {enemy_map_definition}")
                enemy_info = enemy_mapping.get(enemy_map_definition.get("id"))
                print(enemy_info)
                enemy_pos = enemy_map_definition.get("position")
                enemy_info['positions'] = [[enemy_pos[0],enemy_pos[1]]]
                if enemy_info:
                    enemies_info.append(enemy_info)

            # Save the full enemy information to enemies.json
            enemies_file_path = os.path.join(enemy_layer_path, 'enemies.json')
            with open(enemies_file_path, 'w') as f:
                json.dump(enemies_info, f, indent=4)



    print(f"Level '{level_name}' saved successfully.")



screen, clock, font, level_data = initialize_game()  # Initialize the game with user-defined settings
#load_and_scale_images()  # Load and scale images according to the new TILE_SIZE
run_editor()  # Start the editor with the initialized settings

