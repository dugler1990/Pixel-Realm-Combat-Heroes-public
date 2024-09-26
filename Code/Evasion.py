import pygame
from IceClone import IceClone

class EvasionPlayer:
    def __init__(self, animation_player,create_trap_callback):
        self.animation_player = animation_player
        self.slide_cost = 2  # Define slide_cost as required, can be adjusted
        self.create_trap = create_trap_callback


    def slide(self, player, direction) :#, on_move_callback=None ):
        if "slide" in player.status:
            particle_effect = player.status # slide_right or slide_left
            self.animation_player.create_particles( particle_effect, player.rect.center, player.groups())
        else:
            if player.energy >= self.slide_cost:
                player.energy -= self.slide_cost
                player.status = f"slide_{direction}"
                particle_effect = player.status # slide_right or slide_left
                player.frame_index = 0  
                self.animation_player.create_particles( particle_effect, player.rect.center, player.groups())
                player.set_speed_multiplier(3)
                current_time = pygame.time.get_ticks()
                player.slide_end_time = current_time + player.slide_duration
                player.rect.y += 20
                player.hitbox.center = player.rect.center
    
                # # Invoke callback each time the player moves while sliding
                # if on_move_callback:
                #     print("IN ON MOVE CALLBACK CONDITIONAL")
                #     on_move_callback(player)
                
    def create_ice_clone(self, player, effect_type='freeze', lifespan=3000, radius=5):
        if player.energy >= self.slide_cost:
            player.energy -= self.slide_cost
            trap_config = {
                'class': IceClone,
                'pos': player.rect.center,
                'groups': player.groups(),  # Adjust as necessary
                'image_path': '../Graphics/Traps/Ice/ice_clone.png',
                'effect_type': effect_type,
                'trigger':'proximity',
                'death_animation':'ice_clone_death_1',
                'lifespan': lifespan,
                'radius': radius,
                'health': 100,
                'exp_value': 50
            }
            self.create_trap(trap_config)