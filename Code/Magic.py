import pygame
from Settings import *
from random import randint
import os


# This is for file (images specifically) importing (This line changes the directory to where the project is saved)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player
        self.sounds = {
            "heal": pygame.mixer.Sound("../Audio/Heal.wav"), 
            "flame": pygame.mixer.Sound("../Audio/Fire.wav"),
            "ice": pygame.mixer.Sound("../Audio/ice.wav"),            
        }

    def heal(self, player, strength, cost, groups):
        if player.energy >= cost:
            self.sounds["heal"].play()
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats["health"]:
                player.health = player.stats["health"]
            self.animation_player.create_particles("aura", player.rect.center, groups)
            self.animation_player.create_particles("heal", player.rect.center + pygame.math.Vector2(0, -60), groups)

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds["flame"].play()

            if player.status.split("_")[0] == "right": direction = pygame.math.Vector2(1, 0)
            elif player.status.split("_")[0] == "left": direction = pygame.math.Vector2(-1, 0)
            elif player.status.split("_")[0] == "up": direction = pygame.math.Vector2(0, -1)
            else: direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x: # Horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups)
                else: # Vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups, is_moving=False)
    
    
    def ice_ball(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds["ice"].play()
            direction = player.status.split("_")[0]
            for i in range(1, 7):
                offset = pygame.math.Vector2((i if direction in ['right', 'left'] else 0) * (1 if direction == 'right' else -1),
                                             (i if direction in ['up', 'down'] else 0) * (1 if direction == 'down' else -1)) * TILESIZE
                pos = (player.rect.centerx + offset.x, player.rect.centery + offset.y)
                self.animation_player.create_particles( animation_type = f"ice_ball_{direction}_{i}",
                                                        pos=pos,
                                                        groups=groups,
                                                        animation_speed = 250)
                            
    def ice_ball2(self, player, cost, groups, quad_tree):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds["ice"].play()
            direction = player.status.split("_")[0]
            movement = pygame.math.Vector2((1 if direction == 'right' else -1 if direction == 'left' else 0),
                                           (1 if direction == 'down' else -1 if direction == 'up' else 0)) * (TILESIZE/8)
            frame_duration = 10  # Duration each frame is displayed
            total_distance = 6 * TILESIZE  # Total distance to move
            animation_type = f"ice_ball_{direction}"  # Start with the first frame for simplicity

            pos = (player.rect.centerx, player.rect.centery)
            particle = self.animation_player.create_particles(animation_type=animation_type,
                                                    pos=pos,
                                                    groups=groups,
                                                    quadtree = quad_tree,
                                                    movement=movement,
                                                    total_distance=total_distance,
                                                    frame_duration=frame_duration,                                                    
                                                    is_moving=True)
            return particle

              
                
                
                    