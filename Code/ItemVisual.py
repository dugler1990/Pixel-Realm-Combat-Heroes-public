import pygame
from Settings import TILESIZE
class ItemVisual(pygame.sprite.Sprite):
    def __init__(self, item, groups):
        super().__init__(groups)
        self.item = item  # Reference to the logical item
        image_raw = pygame.image.load(item.image_path).convert_alpha()
        self.image = scale_image_to_tile( image_raw, TILESIZE/2 )
        #print("Placing Item Visual At : item pos:")
        #print(item.pos)
        self.rect = self.image.get_rect(topleft=item.pos)
        self.float_offset = item.float_offset
        self.float_direction = item.float_direction
        self.float_speed = item.float_speed
        self.float_amplitude = item.float_amplitude


    def update(self, dt=None):
        self.float_effect()

    def float_effect(self):
        # This method makes the item visually float up and down
        self.float_offset += self.float_direction * self.float_speed  # Adjust float speed
        if abs(self.float_offset) > self.float_amplitude:  # Adjust float range
            self.float_direction *= -1
        self.rect.y += self.float_offset

    # Should not be a part of this class really
def scale_image_to_tile(image, tile_size):
    image_width, image_height = image.get_size()
    aspect_ratio = image_width / image_height

    # Determine which dimension is more restrictive
    if aspect_ratio > 1:
        # Image is wider than tall, fit to width
        new_width = tile_size
        new_height = int(tile_size / aspect_ratio)
    else:
        # Image is taller than wide, fit to height
        new_height = tile_size
        new_width = int(tile_size * aspect_ratio)

    # Scale the image to the new dimensions
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    return scaled_image
