import pygame
class Trigger(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, destination_layout, new_player_position):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)  # Define the trigger area with position and size
        self.destination_layout = destination_layout  # Store the destination layout name or identifier
        self.new_player_position = new_player_position
