import pygame
import random
from Support import import_folder
from Settings import TILESIZE

from hashRect import HashableRect
from NeutralCharacter import NeutralCharacter

class PolarBear(NeutralCharacter):
    def __init__(self,
                 pos,
                 groups,
                 obstacle_sprites,
                 get_tile_valid_actions_callback,
                 update_item_spawner_callback,
                 update_tile_image_callback,
                 trigger_death_particles,#also callback
                 interactable_tile_types,
                 sprite_type="polarbear", # TODO : overwritten in stupid way, eliminate redundancy  
                 health=100,
                 layout_callback_update_quad_tree = None):
        super().__init__(pos,
                         groups,
                         obstacle_sprites, 
                         get_tile_valid_actions_callback, 
                         sprite_type,
                         health,
                         interactable_tile_types,
                         layout_callback_update_quad_tree = layout_callback_update_quad_tree)
        self.trigger_death_particles = trigger_death_particles
        self.sprite_type = 'PolarBear'
        self.import_graphics()  # Load sprite animations
        
        #print(f"self.animations in int : {self.animations}")
        self.image = self.animations['idle'][0]  # Default image
        self.rect = self.image.get_rect(topleft=pos)  # Sprite position
        self.hitbox = self.rect.inflate(0, -10) 
        self.direction = pygame.math.Vector2() 
        self.obstacle_sprites = obstacle_sprites 
        self.update_item_spawner = update_item_spawner_callback
        self.update_tile_image = update_tile_image_callback
        self.fishing_timer = 0
        self.fishing_duration = random.randint(5, 10)  # Random fishing duration between 10 to 30 seconds
        self.building_timer = 0
        self.building_duration = 3  # 10 seconds to build a fishing hole
        self.speed = 1
        self.ice_holes = {} 
        self.ice_hole_duration = 20  # Ice hole closes after 20 seconds of no fishing
        self.hit_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        self.death_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        self.drinking_timer = 0
        self.drinking_time = 15
        self.drinking_cooldown = 100
        self.drinking_cooldown_timer = 100
        
        #override
        self.animation_speed = 0.05
        self.roam_direction_change_coef = 0.01
        self.roam_walk_chance = 0.15
        self.interact_only_on_tile_below = False

    def check_death(self):
        if self.health <= 0:
            self.layout_callback_update_quad_tree( obstacle_sprite = HashableRect( self.rect, self.id ),
                                                   remove_existing= True,
                                                   alive = False )
            self.kill()
            #### TODO , add frozen or not end to monster name for frozen death particles.
            self.trigger_death_particles(self.rect.center, self.sprite_type)
            
            # REMOVE KARMA IF NECESSARY ( how do drops work with enemes, maybe h should drop too.)
            
            self.death_sound.play()

    def import_graphics(self):
        self.animations = {"idle": [], "walking": [], "drinking_water":[]}
        main_path = f"../Graphics/Neutral/PolarBear/"
        target_size = (TILESIZE*2, TILESIZE) 

        for animation in self.animations.keys():
            full_path = main_path + animation
            frames = import_folder(full_path)
            scaled_frames = [pygame.transform.scale(frame, target_size) for frame in frames]
            self.animations[animation] = scaled_frames


    
    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == "weapon":
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            #self.vulnerable = False

    def perform_action(self, action, position):
        #print(f"action : {action}")
        if action == "drink_water" and self.status != 'drinking_water' and self.drinking_cooldown_timer > self.drinking_cooldown:
            self.status = "drinking_water"
            self.drinking_timer = 0  
            
            # TODO: Just need to face the water 
    def drink_water(self,dt):
        
        #print("DRINKING WATER FOR")
        #print(self.drinking_timer)
        self.drinking_timer += dt
        if self.drinking_timer > self.drinking_time:
            self.status = 'walking'
            self.drinking_cooldown_timer = 0


    # def build(self, dt):
    #     self.building_timer += dt
    #     if self.building_timer >= self.building_duration:
            
    #         #tile_position = self.rect.center
    #         #tile_position = ( (tile_position[0] // TILESIZE) * TILESIZE, (tile_position[1] // TILESIZE) * TILESIZE )

    #         self.status = "fishing"
    #         self.fishing_timer = 0  # Reset fishing timer
    #         # Update tile image to a completed fishing hole
    #         #fishing_hole_pos = self.get_front_tile_position()
    #         self.update_tile_image("fishing_hole", self.adapted_tile_position )

    # def fish(self, dt):
    #     self.fishing_timer += dt
    #     if self.fishing_timer >= self.fishing_duration:
    #         self.status = "walking"  # Return to roaming behavior
    #         #self.ice_hole_timer = 0
    #     else:
            
    #         # Reset the ice hole timer for the hole being actively fished
    #         if self.adapted_tile_position in self.ice_holes:
    #             self.ice_holes[self.adapted_tile_position] = self.ice_hole_duration # This does limit fishing to the last hole made, no finding holes atm.

    #         if random.random() < 0.1:  # Adjust spawn chance as needed
    #             self.spawn_fish_item()

    # def spawn_fish_item(self):
    #     # Define fish item spawn positions around the Eskimo
    #     #print(" \n \n SPAWN FISH \n \n")
    #     fish_positions = [[self.rect.x + offset[0], self.rect.y + offset[1]] for offset in [(-32, 0), (32, 0), (0, -32), (0, 32)]]
    #     random_position = random.choice(fish_positions)
    #     #print(f"Random position : {[random_position]}")
    #     # Update fish item spawn positions using the callback
    #     self.update_item_spawner("frozen_fish", [random_position])

    def get_front_tile_position(self):
        # Determine the tile position in front of the Eskimo based on current direction
        direction = self.direction if self.direction.magnitude() != 0 else pygame.math.Vector2(1, 0)
        front_tile_pos = (self.rect.centerx + direction.x * 32, self.rect.centery + direction.y * 32)
        return front_tile_pos

    #@profile
    def update(self, dt, QuadTree,entity_quad_tree):
        
        #print(f"health: {self.health}")
       # print("Eskimo still updating")
       # print(self.status)
       # print(dt)
       # print(self.building_timer)
       # print(self.fishing_timer)
        self.check_death()
        if self.status == 'drinking_water':
            self.drink_water(dt)
        else:
            #print(f"DT IN POLAR BEAR : {dt}")
            self.drinking_cooldown_timer += dt
        super().update(dt,QuadTree,entity_quad_tree)  

