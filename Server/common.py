# common.py

import pygame
class Player:
    def __init__(self, id, name, position):
        self.id = id
        self.name = name
        self.position = position

    def handle_input(self, input_data):
        if input_data['type'] == pygame.KEYDOWN:
            if input_data['key'] == pygame.K_LEFT:
                self.position[0] -= 5
            elif input_data['key'] == pygame.K_RIGHT:
                self.position[0] += 5
            elif input_data['key'] == pygame.K_UP:
                self.position[1] -= 5
            elif input_data['key'] == pygame.K_DOWN:
                self.position[1] += 5
        elif input_data['type'] == pygame.KEYUP:
            # Handle key releases if necessary
            pass

class GameState:
    def __init__(self):
        self.players = {}
