import pygame
import random
from Support import import_folder
from Settings import TILESIZE
from hashRect import HashableRect

from NeutralCharacter import NeutralCharacter
class Eskimo(NeutralCharacter):
    def __init__(self,
                 pos,
                 groups,
                 obstacle_sprites,
                 get_tile_valid_actions_callback,
                 update_item_spawner_callback,
                 update_tile_image_callback,
                 trigger_death_particles,#also callback
                 interactable_tile_types,
                 sprite_type="eskimo", 
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
        self.sprite_type = 'Eskimo'
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
        self.speed = 2
        self.ice_holes = {} 
        self.ice_hole_duration = 20  # Ice hole closes after 20 seconds of no fishing
        self.hit_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        self.death_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        



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
        self.animations = {"idle": [], "walking": [], "fishing": [], "building": [], "building_in_progress": []}
        main_path = f"../Graphics/Neutral/Eskimo/"
        target_size = (TILESIZE, TILESIZE) 

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

    def perform_action(self, action, tile_position):
        if action == "create_fishing_hole":
            self.status = "building"
            self.building_timer = 0  
            self.update_tile_image("building_in_progress", tile_position)
            self.adapted_tile_position =  tile_position # Keep for consistently of placing of changed tiles Probly not the most elegant
            self.ice_holes[tile_position] = self.ice_hole_duration  
        # Set Eskimo's position to the left edge of the current tile
        # Assuming tile_position is the top-left corner of the target tile
            new_x = tile_position[0] - TILESIZE  # Move one tile to the left
            new_y = tile_position[1]  # Keep the y position the same
            
        # Directly update Eskimo's position
            self.rect.x = new_x
            self.rect.y = new_y
            self.hitbox.x = new_x  # Update the hitbox as well if necessary
            self.hitbox.y = new_y



    def build(self, dt):
        self.building_timer += dt
        if self.building_timer >= self.building_duration:
            
            #tile_position = self.rect.center
            #tile_position = ( (tile_position[0] // TILESIZE) * TILESIZE, (tile_position[1] // TILESIZE) * TILESIZE )

            self.status = "fishing"
            self.fishing_timer = 0  # Reset fishing timer
            # Update tile image to a completed fishing hole
            #fishing_hole_pos = self.get_front_tile_position()
            self.update_tile_image("fishing_hole", self.adapted_tile_position )

    def fish(self, dt):
        self.fishing_timer += dt
        if self.fishing_timer >= self.fishing_duration:
            self.status = "walking"  # Return to roaming behavior
            #self.ice_hole_timer = 0
        else:
            
            # Reset the ice hole timer for the hole being actively fished
            if self.adapted_tile_position in self.ice_holes:
                self.ice_holes[self.adapted_tile_position] = self.ice_hole_duration # This does limit fishing to the last hole made, no finding holes atm.

            if random.random() < 0.1:  # Adjust spawn chance as needed
                self.spawn_fish_item()

    def spawn_fish_item(self):
        # Define fish item spawn positions around the Eskimo
        #print(" \n \n SPAWN FISH \n \n")
        fish_positions = [[self.rect.x + offset[0], self.rect.y + offset[1]] for offset in [(-32, 0), (32, 0), (0, -32), (0, 32)]]
        random_position = random.choice(fish_positions)
        #print(f"Random position : {[random_position]}")
        # Update fish item spawn positions using the callback
        self.update_item_spawner("frozen_fish", [random_position])

    def get_front_tile_position(self):
        # Determine the tile position in front of the Eskimo based on current direction
        direction = self.direction if self.direction.magnitude() != 0 else pygame.math.Vector2(1, 0)
        front_tile_pos = (self.rect.centerx + direction.x * 32, self.rect.centery + direction.y * 32)
        return front_tile_pos

    #@profile
    def update(self, dt, QuadTree, entity_quad_tree):
    # print(f"health: {self.health}")
       # print("Eskimo still updating")
        #print(self.status)
       # print(dt)
        #print(self.building_timer)
        #print(self.fishing_timer)
        self.check_death()
           # Decrement timers for all ice holes and close them if their time runs out
        for position, timer in list(self.ice_holes.items()):
            #print(self.position,timer)
            self.ice_holes[position] -= dt
            if self.ice_holes[position] <= 0:
                # Time's up, close the ice hole and update the tile image
                self.update_tile_image("ice_tile", position)
                del self.ice_holes[position]     
        # print(self.pos)
        if self.status in ["building", "fishing"]:
            if self.status == "building":
                self.build(dt)
            elif self.status == "fishing":
                self.fish(dt)
        else:
            super().update(dt,QuadTree,entity_quad_tree)  

