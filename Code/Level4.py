### Plan here is to make a Level class that uses Layout classes to 
#   re-render the level when a <trigger> (door) is stepped on.
from Eskimo import Eskimo
import json
from Spawner import Spawner
from ItemSpawner import ItemSpawner
from Item import Item
from ItemVisual import ItemVisual
import pygame
from Settings import *
from Tile import Tile
from Trigger import Trigger
from Player import SpecificPlayer
from Debug import debug
from Support import *
from random import choice, randint
from Weapon import Weapon
from UI import UI
from Enemy import Enemy
from Particles import AnimationPlayer
from Magic import MagicPlayer
from Evasion import EvasionPlayer
from Upgrade import Upgrade
import os
import random
from AnimationSprite import AnimationSprite
from Trap import Trap
from Tree import Tree 
from Weather import Weather
from AnimatedEnvironmentSprite import AnimatedEnvironmentSprite
from WaterTile import WaterTile
from WeatherOverlay import WeatherOverlay
from DaytimeBrightnessOverlay import DaytimeBrightnessOverlay
import math
from GrassManager import GrassManager
from QuadTree import QuadTree
from QuadTree import QuadTreeManager
from QuadTreeItem import QuadTreeItem

from hashRect import HashableRect
from Entity import Entity

#with open('triggers.json',r) as file
#triggers = json.loads(file.read())




### Layouts will be instanciated with a path to its triggers fill

class LayoutManager:
    def __init__(self, 
                 selected_player_info_dir,
                 TILESIZE,
                 restore_persistent_enemies_callback=None,
                 initialize_map_items_callback=None
                 ):
        # This class manages layouts of a level with triggers and logs
        # #print(TILESIZE)        
        # self.TILESIZE = TILESIZE
    
        # self.restore_persistent_enemies_callback = restore_persistent_enemies_callback        
        # self.ground_sprites = pygame.sprite.Group()
        # self.selected_player_info_dir = selected_player_info_dir        
        # self.grass_manager = grass_manager = GrassManager(grass_path="../Graphics/Grass",
        #                                                   tile_size=TILESIZE,
        #                                                   stiffness=600,
        #                                                   max_unique=3, 
        #                                                   place_range=[0, 1])
        # #self.grass_manager.enable_ground_shadows(shadow_radius=4, shadow_color=(0, 0, 1), shadow_shift=(1, 2))
        # self.visible_sprites = YSortCameraGroup(self.ground_sprites, self.grass_manager)
        # self.obstacle_sprites = pygame.sprite.Group()
        # self.trigger_sprites = pygame.sprite.Group() 
        # self.animation_active = False    
        # self.player = None 
        # self.initialize_map_items_callback= initialize_map_items_callback
        # self.tile_map = {} 
        # self.daytime_brightness_overlay = DaytimeBrightnessOverlay()
        # Enable Ground Shadows
        #self.grass_manager.enable_ground_shadows(shadow_strength=40, shadow_radius=2, shadow_color=(0, 0, 1), shadow_shift=(0, 0))

        self.start_map_layout(selected_player_info_dir = selected_player_info_dir,
                        TILESIZE = TILESIZE,
                        restore_persistent_enemies_callback=restore_persistent_enemies_callback,
                        initialize_map_items_callback=initialize_map_items_callback)

    def start_map_layout(self,
                         selected_player_info_dir,
                         TILESIZE,
                         restore_persistent_enemies_callback=None,
                         initialize_map_items_callback=None,
                         Player = None, 
                         daytime_layout = True,
                         prepared_daytimeoverlay = None):# this last param sucks, showing how bad my map change logic is.
        # This function initializes the LayoutManager instance
        self.TILESIZE = TILESIZE
        self.csv_layout_width = 40* TILESIZE # TODO hard coded atm, i am not sure exactly how to configure this config ( i am initializing the QuadTree before accessing layout csvs thats the only issue, initialize it after and keep that info)
        self.csv_layout_height = 40* TILESIZE

        #print(f"self.obstacle_quad_tree : {self.obstacle_quad_tree.cx}")
        self.selected_player_info_dir = selected_player_info_dir
        self.restore_persistent_enemies_callback = restore_persistent_enemies_callback
    
        # Initialize grass manager
        self.grass_manager = GrassManager(grass_path="../Graphics/Grass", tile_size=TILESIZE, stiffness=600, max_unique=3, place_range=[0, 1])
    
        # Initialize sprite groups
        self.ground_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.trigger_sprites = pygame.sprite.Group()
        self.overhead_areas = []
    
        # Initialize camera group for sorting sprites
        self.visible_sprites = YSortCameraGroup(self.ground_sprites, self.grass_manager, self.overhead_areas)
    
       # Positioning here again, its a bit of a mess , i think i do this in start map of level first and it gets reset here unwillingly so i set it again
       
        self.daytime_layout = daytime_layout
        # Set animation flag
        self.animation_active = False
    
    
        # Setup timer
        
        self.start_ticks = pygame.time.get_ticks()
        

    
        # Initialize player and callback
        self.player = Player
        
        self.initialize_map_items_callback = initialize_map_items_callback
    
        # Initialize tile map and daytime brightness overlay
        self.tile_map = {}
        
        #print(f"daytime layout : {daytime_layout}")
        #print(type(daytime_layout))
        if self.daytime_layout:
            if prepared_daytimeoverlay:
                self.daytime_brightness_overlay = prepared_daytimeoverlay
            else: 
                self.daytime_brightness_overlay = DaytimeBrightnessOverlay()
        else: self.daytime_brightness_overlay = None
        #print(f"resulting daytime overlay value : {self.daytime_brightness_overlay}")
    
    
    def display_time( self, display_surface):
        # Calculate elapsed time in milliseconds
        elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        elapsed_seconds = elapsed_ticks // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
    
        # Format time as MM:SS
        time_string = f"{minutes:02}:{seconds:02}"
        
        # Render time string
        text_surface = pygame.font.Font(None, 36).render(time_string, True, (255, 255, 255))
        
        # Position the text at the top-left corner
        
        display_surface.blit(text_surface, (display_surface.get_size()[0]/2, 10))
    
    
    def add_obstacle_sprite_to_quad_tree(self, obstacle_sprite, alive=True, remove_existing = True):
        
        
        ## This is a mess im controlling things here and then also in the quadtree methods
        #  Needs cleanup
        #print(type(obstacle_sprite))
        #print(isinstance(obstacle_sprite,Entity))
        #if  remove_existing:
        #    print(" is netity and remove existing and passed condition ")
        #    self.entity_quad_tree.manager.remove( obstacle_sprite._id, remove_existing )
        #if alive:
        #print(f"alive : {alive}")
        # Add the obstacle sprite to the quadtree
        self.entity_quad_tree.insert(obstacle_sprite, 
                                     alive = alive,
                                     remove_existing=remove_existing
                                     )
        
            # The above is quite confusing, the insert method actually doesnt insert if alive is false,
            # the insert method deletes every time, if remove_existing is true
            

    def remove_obstacle_sprite_from_quad_tree(self, obstacle_sprite):# not used at the moment
        # Remove the obstacle sprite from the quadtree
        self.obstacle_quad_tree.delete(obstacle_sprite)

    def set_player(self, player):
        """Sets the player object for layout interaction."""
        self.player = player


    def trigger_animation(self, frames, position, speed):
        AnimationSprite(frames, position, speed, [self.visible_sprites])


    def set_spawner(self, spawner, layout_callback_update_quad_tree):
        """Sets the Spawner object for enemy management."""
        self.spawner = spawner  
        self.spawner.set_layout_callback_update_quad_tree( layout_callback_update_quad_tree )

    def add_item_visual(self, item):
        """Convert Item to ItemVisual and add to visible_sprites."""
         
        item_visual = ItemVisual(item=item, groups=[self.visible_sprites])
        
        #print(f"Item attempted to be added to visual sprites: {item_visual}")
        self.visible_sprites.add(item_visual)

    def initialize_layout(self,
                          layout_path,player_position=None,
                          restart = False, 
                          Player = None,
                          daytime_layout=False, 
                          prepared_daytimeoverlay = None):  

       #print(f"  Player position in initialize layout : {player_position}")
        
        self.spawner.spawn_areas = [] # each layout start fresh spawn areas if any.ofc.
        #print(f"starting layout : {layout_path}")        
        # Clear existing sprites from groups
        self.ground_sprites.empty()
        self.visible_sprites.empty()
        self.trigger_sprites.empty()
        self.obstacle_sprites.empty()
        self.last_trigger_time = None
        if restart:
            self.start_map_layout(selected_player_info_dir = self.selected_player_info_dir,
                            TILESIZE = TILESIZE,
                            restore_persistent_enemies_callback=self.restore_persistent_enemies_callback,
                            initialize_map_items_callback=self.initialize_map_items_callback, 
                            daytime_layout=daytime_layout,
                            Player = Player,
                            prepared_daytimeoverlay = prepared_daytimeoverlay)
        



        
        # Tile Layouts from .csv scaled tiles and dictionary.
        #print(os.listdir())
        #print(layout_path)

        layout_layers = os.listdir(layout_path)
        layout_layers = [layer for layer in layout_layers if '.' not in layer]
        for layer in layout_layers:
            #print("\n \n LAYER \n \n")
            #print(layer)
            if layer in ["Objects","Enemies","Items"]: continue
            with open(f"{layout_path}/{layer}/{layer}_layer_definition.json","r") as f : 
                layout_definition_dict = json.load(f)
            if os.path.exists(f"{layout_path}/{layer}/Objects" ):
                self.instantiate_objects( f"{layout_path}/{layer}/Objects" )
            if os.path.exists(f"{layout_path}/{layer}/Items"):
                item_config_path = f"{layout_path}/{layer}/Items/initial_map_items.json"
                if self.initialize_map_items_callback:
                    #print(f"item_config_path:{item_config_path}")
                    self.initialize_map_items_callback(item_config_path)

            
            self.instantiate_layout_layer( layout_definition_dict )
            
            self.visible_sprites.set_overhead_areas(self.overhead_areas)
                   
            # Instantiate Enemies
 
            #print(f"ATTEMPT TO DRAW ENEMIES FOR LAYER: {layout_path}")
            if os.path.exists(f"{layout_path}/{layer}/Enemies"):
                self.instantiate_enemies( f"{layout_path}/{layer}/Enemies", self.spawner )
            if os.path.exists(f"{layout_path}/{layer}/NeutralCharacters/NeutralCharacters.json"):
                self.instantiate_neutral_characters(f"{layout_path}/{layer}/NeutralCharacters/NeutralCharacters.json")
        
        # Use the callback to restore persistent enemies for the layout
        if self.restore_persistent_enemies_callback:
            self.restore_persistent_enemies_callback(layout_path)

        
        # Buildings and other sprites plus obstruction blocks
       
        # THIS IS FOR VERSION THAT HAS A SINGLE CENTRAL OBJECTS FOLDER AS IF IT WERE A LAYER ITSELF. ( ORIGINAL LEVEL 4 works like this (map4))
        #self.instantiate_objects( f"{layout_path}/Objects" )

    #print out the ground sprites details


        #print("\nGround Sprites:")
        #for sprite in self.ground_sprites:
           #print(f"Sprite: {sprite}, Position: {sprite.rect.topleft}, Size: {sprite.rect.size}")
          
            # Not sure about this.
            ## Not sure if i am re adding this actually.
            #self.obstacle_sprites.add(self.player)
            
        items = []
        for sprite in self.obstacle_sprites:
            #left, top, width, height = sprite.rect
            #right = left + width
            #bottom = top + height
            
            if hasattr(sprite, "mask"):
                mask = sprite.mask
            else: mask = None
            
            item = HashableRect(sprite.rect, mask = mask)
            items.append(item)
            
        #print(f"items upon restart layout : {items}")
            
        #print(self.obstacle_sprites)
        #print("restarting quad trees :")
        self.obstacle_quad_tree_manager = QuadTreeManager()
        self.obstacle_quad_tree = QuadTree(items = items,
                                           depth=8,
                                           bounding_rect=pygame.rect.Rect(0,0,self.csv_layout_width,self.csv_layout_height),
                                           manager = self.obstacle_quad_tree_manager ) # this would actually need the size of the map bounding_rect=(0, 0, HEIGHT, WIDTH)
        self.entity_quad_tree_manager = QuadTreeManager()
        self.entity_quad_tree = QuadTree(items = [],
                                           depth=8,
                                           bounding_rect=pygame.rect.Rect(0,0,self.csv_layout_width,self.csv_layout_height),
                                           manager = self.entity_quad_tree_manager ) # this would actually need the size of the map bounding_rect=(0, 0, HEIGHT, WIDTH)
                

        #print(f"resulting changed quad trees  (should be empty): {self.entity_quad_tree.manager.item_mapping}")
        #print(f"resulting changed quad trees  (should be empty): {self.obstacle_quad_tree}")

        
        if player_position:
            #print(f"player_position in instantiate layout:{player_position}")
            # Reset player's directional attributes
            #self.player.direction.x = 0
            #self.player.direction.y = 0
        
            # Reset player's status to a known state
            #self.player.status = "down_idle"  # Or any other default idle state
        
            self.player.rect.topleft = player_position
            self.player.hitbox.topleft = player_position
            self.player.update(layout_switch = False,
                               QuadTree=self.obstacle_quad_tree,
                               entity_quad_tree= self.entity_quad_tree)
            self.visible_sprites.add(self.player) 


    def update_tile_image(self, key, position):
        """
        Update the image of a tile at the given position based on the provided key.
    
        :param key: A string key representing the new tile image to use.
        :param position: A tuple (x, y) representing the tile's position on the map.
        """
        # Define a dictionary mapping keys to their corresponding image paths
        image_mapping = {
            "building_in_progress": {"image_path":"../Graphics/Tiles/building_in_progress.png",
                                     "valid_interaction_types":[], 
                                      "is_obstacle" : True},
            "fishing_hole": {"image_path":"../Graphics/Tiles/fishing_hole.png",
                             "valid_interaction_types":[],
                              "is_obstacle" : True},
            "ice_tile":{"image_path":"../Graphics/Tiles/ice_tile.png",
                        "valid_interaction_types":["create_fishing_hole"],
                          "is_obstacle" : False} #### Should be a part of Tile.py really...maybe...            

                         }

        # Find the tile image path based on the provided key
        image_path = image_mapping.get(key).get("image_path")
        if not image_path:
            #print(f"No image found for key: {key}")
            return
        valid_interaction_types = image_mapping.get(key).get("valid_interaction_types")
        is_obstacle = image_mapping.get(key).get("is_obstacle")

        # Load the new image
        new_image = pygame.image.load(image_path).convert()
        new_image = pygame.transform.scale(new_image, (self.TILESIZE, self.TILESIZE))
        #print(f"position attempted to be found in update_tile_image : {position}")
        # Find the tile at the specified position
        tile = self.tile_map.get(position)
        
        if tile:
            # Remove the tile from all sprite groups to ensure the update is reflected
           
            groups = tile.groups()
            
            #print("Tile Groups")
            #print( groups )
            #print(" groups dir : ")
            #print( dir(groups[0]) )

            for group in groups:
                group.remove(tile)

            # Update the tile's image
            tile.image = new_image
            tile.valid_interaction_types = valid_interaction_types

            #print("Tile Groups")
            #print( groups )

            # Re-add the tile to all sprite groups
            for group in groups:
                #print(group)
                if group is self.obstacle_sprites:continue
                group.add(tile)

            if is_obstacle:
                # If the tile should be an obstacle, add it to the obstacle_sprites group
                self.obstacle_sprites.add(tile)

            
            # Update only the changed tile on the ground surface
            self.visible_sprites.update_tile_on_ground_surface(tile)

        else:
           #print(f"No tile found at position: {position}")
            pass




    def instantiate_objects(self, objects_path):
        # Check if the object_info.json file exists in the given objects_path
        object_info_path = os.path.join(objects_path, "object_info.json")
        if os.path.exists(object_info_path):
            # Open and read the object_info.json file
            with open(object_info_path, 'r') as file:
                objects_info = json.load(file)
        
            # Iterate over each object defined in the JSON file
           
            for obj_info in objects_info:
                object_image_path = obj_info.get("image_path")
                object_details = obj_info.get("object_info")
            
                # Assuming you have a function or method to handle the instantiation of an individual object
                self.instantiate_object(object_image_path, object_details)


    def instantiate_object(self, image_path, object_info):
        
        #print("creating object")
        
        image = pygame.image.load(image_path).convert_alpha()
        image_tile_width = object_info.get("width")
        image_tile_height = object_info.get("height")
        image = pygame.transform.scale(image, (self.TILESIZE * image_tile_width, self.TILESIZE * image_tile_height))
    
        image_x_pos = object_info.get("x_pos") * self.TILESIZE
        image_y_pos = object_info.get("y_pos") * self.TILESIZE
    
        # Dynamic handling based on type
        object_type = object_info.get("type",'')
        #print(f"object info:{object_info}")
        if object_type == "tree": 
            
            sprite_animation_config = object_info.get("sprite_animation_config")
            #print(f"ATTEMPTING TO CREATE TREE    config:{sprite_animation_config}")
            self.instantiate_tree(image_x_pos, image_y_pos, sprite_animation_config)
        else:
            Tile((image_x_pos, image_y_pos), [self.visible_sprites], "object", image)
    
        # Common methods for all objects
        self.handle_obstruction_matrix(image_x_pos,
                                       image_y_pos,
                                       object_info,
                                       image,
                                       mask_indicator=True)
        self.handle_spawn_area(image_x_pos, image_y_pos, object_info)
        self.handle_triggers(image_x_pos, image_y_pos, object_info)
    
    def instantiate_tree(self, x_pos, y_pos, sprite_animation_config):
        
        Tree((x_pos, y_pos), [self.visible_sprites, self.obstacle_sprites], sprite_animation_config)
        
    
    def handle_overhead_area(self,
                             x_pos,
                             y_pos,
                             object_info,
                             image,# TODO: not being passed......dno why its here, in below functino too 
                             tile_size_divisor):
        
        used_tile_size = self.TILESIZE / tile_size_divisor 
#        print(f"intiial overhead def : {object_info}")
        overhead_matrix = object_info.get("overhead_definition_path", [])
        
        if overhead_matrix != []:
            overhead_matrix = import_csv_layout(overhead_matrix)
            
        else:
            overhead_matrix = object_info.get('overhead_matrix',[])
        
        #print(f"overhead matrix: {overhead_matrix}")
        #print(f"dimensy :{len(overhead_matrix)}")
        y = -1 # TODO: unecessary , i just got a litttle lost, needs cleanup
        for y_ , row in enumerate( overhead_matrix ):
            y+=1
            x=-1
            #print(f"row : {overhead_matrix}")
            #print(f"row : {len(overhead_matrix)}")
            
            for x_ , cell in enumerate(row):
                x += 1
                #cell = cell[1]
                #print(f"cell : {cell}, type: {type(cell)}")
                if int(cell) == 1 :
                    
                    #print("hit on overhead_areas")
                    
                                        # Calculate the position of the overhead area
                    overhead_x = x_pos + (x * used_tile_size)
                    overhead_y = y_pos + (y * used_tile_size)
                    # Create a rect for the overhead area
                    overhead_rect = pygame.Rect(overhead_x+1, overhead_y+1, used_tile_size+1, used_tile_size+1)
                    # Extract the corresponding image section
                    image_section = image.subsurface(pygame.Rect((x * used_tile_size) +1, (y * used_tile_size) +1, used_tile_size+1, used_tile_size+1))
                    # Add the rect and image section to the overhead areas list
                    self.overhead_areas.append((overhead_rect, image_section))
        
    
    def handle_obstruction_matrix(self,
                                  x_pos,
                                  y_pos,
                                  object_info,
                                  image,
                                  tile_size_divisor=1,
                                  mask_indicator=False):
        
        

        
        used_tile_size = self.TILESIZE / tile_size_divisor # allows for smaller grain obstruction matrix
        obstacle_image = pygame.image.load( "../levels/Map4/ice_palace_2/ground/Objects/object_images/invisible_trigger.png" ).convert_alpha()
        obstacle_image = pygame.transform.scale( obstacle_image , (used_tile_size, used_tile_size) ) 
        #print("in obstruction matrix")
        
        
        ### Error is here, i was previously just getting attribute from object info, 
          # in the new use case for a scaled object, we are using .csvs just need a new if.
          # TODO This is a solid principles breach i think . interms of bad config...D?
        
        obstruction_matrix = object_info.get("csv_definition_path", [])
        
        if obstruction_matrix != []:
            obstruction_matrix = import_csv_layout(obstruction_matrix)
            
        else:
            obstruction_matrix = object_info.get('obstruction_matrix',[])
        
        #print(obstruction_matrix)
        #print(image.get_abs_offset())
        #print(image.get_size())
        #print(x_pos,y_pos)
        
        y_count = 0
        for y_offset, row in enumerate(obstruction_matrix, start=-1):
            y_count += 1
            x_count = 0
            for x_offset, cell in enumerate(row):
                x_count += 1
                if int(cell) == 1:
                    boundary_x = x_pos + (x_offset * used_tile_size)
                    boundary_y = y_pos + (y_offset * used_tile_size)
                    #print(boundary_x, boundary_y)
                    
                    
                    
                    #WL: STILL NO MICRO OBSTRUCTIONS HERE....
                    
                    
                    if mask_indicator:
                        mask = None
                        
                        
                        
                        #print(x_offset,y_offset)
                        #print(x_count,y_count)
                        mask_x =  (x_count -1) * used_tile_size 
                        mask_y  =  (y_count -1) * used_tile_size
                        
                        
                        #print(mask_x, mask_y)
                        # Define the ROI rectangle using the calculated top-left corner and TILESIZE
                        roi_rect = pygame.Rect(mask_x, mask_y , used_tile_size, used_tile_size)
                        
                        #print(roi_rect)
                        #print(dir(roi_rect))
                        
                        # Extract the portion of the image corresponding to the ROI
                        
                        
                        try: # TODO: we have this failing systematically if obstruction matrix is bigger than the size of the object, i dont really do this anyway tho.
                            # Create mask for the tile image
                            tile_image = image.subsurface(roi_rect)
                            mask = pygame.mask.from_surface(tile_image)
                        except:
                            mask = None
                    else:
                        mask = None
                    #print(boundary_x,boundary_y)
                    new_tile = Tile((boundary_x, boundary_y),
                                    [self.obstacle_sprites,self.ground_sprites], 
                                    'ground', # used to be insivible, checking effect
                                    mask = mask,
                                    surface = obstacle_image)
                    #self.add_obstacle_sprite_to_quad_tree(new_tile.rect) only creating QuadTree after initial layout initialization now
                    
    
    def handle_spawn_area(self, x_pos, y_pos, object_info):
        #print("in handlespawnarea")
        if object_info.get('spawn_area'):
            spawn_matrix = object_info.get("spawn_matrix")
            spawner_config_path = object_info.get("spawner_config_path")
            with open(spawner_config_path, 'r') as spawner_file:
                spawner_config = json.load(spawner_file)
                
            #print(f"spawner_config_path:{spawner_config_path}")
            #print(f"spawner_config:{spawner_config}")
            self.spawner.add_spawn_area(spawn_matrix, spawner_config, object_info)
    
    def handle_triggers(self, x_pos, y_pos, object_info):
        #print("in handle triggers")
        
        
        
        trigger_info = object_info.get("trigger_info", None)
        if trigger_info:
            #print(trigger_info)
            trigger_matrix = trigger_info.get("trigger_matrix", [])
            for y_offset, row in enumerate(trigger_matrix):
                for x_offset, cell in enumerate(row):
                    if cell == 1:
                        trigger_x = x_pos + (x_offset * self.TILESIZE)
                        trigger_y = y_pos + (y_offset * self.TILESIZE)
                        trigger = Trigger(trigger_x, trigger_y, self.TILESIZE, self.TILESIZE, trigger_info["destination_layout_path"], trigger_info["new_player_position"])
                        self.trigger_sprites.add(trigger)





    def instantiate_neutral_characters(self, neutral_char_path):
        
        #print("IN THE INSTANTIATE NEUTRAL CHAR LEVEL ")
        with open(neutral_char_path, 'r') as file:
            neutral_char_info = json.load(file)

        for char_def in neutral_char_info:
            char_type = char_def['type']
            positions = char_def['positions']
            attributes = char_def['attributes']

            # Use the Spawner to create neutral characters
            for pos in positions:
                # Prepare the config for the spawner
                config = {
                    'type': char_type,
                    'pos': pos,
                    'attributes': attributes
                }
                # Call the Spawner's method to spawn the neutral character
                self.spawner.spawn_neutral(config)


    
    def instantiate_enemies(self, enemy_path, spawner):


        # Check if the enemy directory exists
        if not os.path.exists(enemy_path):
            #print(f"No enemy directory found at {enemy_path}")
            return
        #print(f"{enemy_path}/enemies.json")
        with open( f"{enemy_path}/enemies.json", "r") as file:
            enemy_info = json.load(file)
            

        
        for enemy_def in enemy_info:
            #print(enemy_def)
            # Extract necessary information for spawning the enemy
            enemy_type = enemy_def.get('type')
            positions = enemy_def.get('positions', [])
            persistent = enemy_def.get('persistent', False)
            can_follow = enemy_def.get('can_follow', False)
            spawn_mode = enemy_def.get('spawn_mode', 'instant')  # Default spawn mode to 'instant'
            spawn_interval = enemy_def.get('spawn_interval', 0)
            spawn_chance = enemy_def.get('spawn_chance', 1.0)
            item_drop_info = enemy_def.get('item_drop_info',None)
            # Depending on the spawn mode, use the spawner to create enemies
            if spawn_mode == 'instant':
                for pos in positions:
                    spawner.spawn_enemy({'type': enemy_type,
                                         'pos': pos, 'persistent': persistent,
                                         'can_follow': can_follow,
                                         'item_drop_info':item_drop_info})

            elif spawn_mode == 'timed':
                spawner.schedule_spawn(enemy_type, positions, spawn_interval, persistent, can_follow)
            elif spawn_mode == 'random':
                spawner.schedule_random_spawn(enemy_type, positions, spawn_chance, persistent, can_follow)
              



    def place_items_on_map(self, items_info):
        #print("IN PLACE ITEM ON MAP")
        for item_info in items_info:
            for position in item_info['positions']:  # Iterate over each position
                # Create an ItemVisual for each position and add it to visible_sprites
                item_visual = ItemVisual(item=item_info['item'], groups=[self.visible_sprites])
                # Convert the position from map grid coordinates to pixels
                item_visual.rect.topleft = (position[0] * self.TILESIZE, position[1] * self.TILESIZE)
                self.visible_sprites.add(item_visual)


    def instantiate_layout_layer(self, layout_definition_dict):
        
        #print(layout_definition_dict)

            
                
            
        layout_definition_dict = layout_definition_dict.get("layouts")
        for layout in layout_definition_dict:
            
            
            # if scaled image.
            layer_type = layout.get( 'layer_type', None )
            
            if layer_type == 'scaled_objects':
            
                scaled_objects = layout.get('scaled_objects',[])
                for object_ in scaled_objects:     
                    
                    image = pygame.image.load(object_.get('image_path')).convert_alpha()
                    image_tile_width = object_.get("width")
                    image_tile_height = object_.get("height")
                    image = pygame.transform.scale(image, (self.TILESIZE * image_tile_width, self.TILESIZE * image_tile_height))
                
                    image_x_pos = object_.get("x_pos") * self.TILESIZE
                    image_y_pos = object_.get("y_pos") * self.TILESIZE
                    
                    Tile((image_x_pos, image_y_pos), [self.ground_sprites], "ground", image)
                    #new_tile = Tile(pos, [self.ground_sprites], 'ground', tile_image, valid_interaction_types)
                    
                    
                    #### Urg , i need to fill in this somehow, i guess creating one big tile 
                    # will not work..
                    
                    # tile_grid[row_index][col_index] = new_tile
                    # self.tile_map[(pos[0], pos[1])] = new_tile
                    
                    ### Its how i draw ground tiles, right ? 
                    
                    
                    
                    obstruction_tile_size_divisor = object_.get( "tile_size_divisor" )
                    canopy_tile_size_divisor = object_.get( "canopy_size_divisor",1 )
                    # Common methods for all objects
                    self.handle_obstruction_matrix(image_x_pos,
                                                   image_y_pos,
                                                   object_,
                                                   image,
                                                   obstruction_tile_size_divisor)
                    self.handle_overhead_area(image_x_pos,
                                               image_y_pos,
                                               object_,
                                               image,
                                               canopy_tile_size_divisor
                                               )
                    self.handle_spawn_area(image_x_pos, image_y_pos, object_)
                    self.handle_triggers(image_x_pos, image_y_pos, object_)
            
            else:
                csv_layout_path = layout.get("csv_layout_path")
                layout_csv = import_csv_layout( csv_layout_path )
                
                sprite_group ='ground'
                tile_grid = [[None for _ in range(len(layout_csv[0]))] for _ in range(len(layout_csv))]  # Prepare a grid to store tile references
                #Note: separated water tiles bcoz they not ground sprites, they animated and we need to instantiate ground b4 animated sprites.
                water_tile_grid = [[None for _ in range(len(layout_csv[0]))] for _ in range(len(layout_csv))]  # Grid specifically for WaterTiles
                if not hasattr(self, "grass_tile_grid") :
                    self.grass_tile_grid = [[None for _ in range(len(layout_csv[0]))] for _ in range(len(layout_csv))]  # Grid specifically for GrassTiles
    
        
                #print(f" layout tiles ! : {layout.get('tiles', [])}")
                # First pass to create all tile instances
                
                #print(f"   HAS THE TILE SIZE CHANGE ????? : {self.TILESIZE}")
                for tile_info in layout.get("tiles", []):
                    
                    tile_image_path = tile_info.get("tile_image_path")
                    if tile_image_path != "irrelevant":
                        tile_image = pygame.image.load(tile_image_path).convert()
                        
                        
                        tile_image = pygame.transform.scale(tile_image, (self.TILESIZE, self.TILESIZE))
                        valid_interaction_types = tile_info.get("valid_interaction_types", [])
            
                    for row_index, row in enumerate(layout_csv):
                        for col_index, val in enumerate(row):
                            if val == str(tile_info["csv_constant_value"]):  # Match the CSV cell value
                                pos = (col_index * self.TILESIZE, row_index * self.TILESIZE)
                                if tile_info.get("type") == "water":
                                    #print(f"water vaid interacions : {valid_interaction_types}")
                                    animation_paths = tile_info.get('animation_config')
                                    # Initialize with a specific animation configuration
                                    animation_config = {
                                        'mild_ripple_neutral': import_folder( animation_paths.get('mild_ripple_neutral') ),
                                        'mild_ripple_left': import_folder(animation_paths.get('mild_ripple_left')),
                                        'mild_ripple_right': import_folder(animation_paths.get('mild_ripple_right')),
                                        'intense_ripple_left': import_folder(animation_paths.get('intense_ripple_left')),
                                        'intense_ripple_right': import_folder(animation_paths.get('intense_ripple_right')),
                                        'calm': import_folder( animation_paths.get('calm'))  # Default animation
                                    }
                                    new_tile = WaterTile(pos, [self.visible_sprites], animation_config, 150)
                                    water_tile_grid[row_index][col_index] = new_tile
                                    #new_tile = Tile(pos, [self.ground_sprites], 'ground', tile_image, valid_interaction_types)
                                    # For now always an obstruction
                                    # add regular water tile below:
                                    self.tile_map[(pos[0], pos[1])] = Tile(pos, [self.ground_sprites], 'ground', tile_image, valid_interaction_types)
                                    Tile(pos, [self.obstacle_sprites], 'invisible')
    #                                pass
                                elif tile_info.get("type") == "grass":
                                   
                                   grass_options = tile_info.get("grass_options", [0,1,2,3,4,5])
                                   grass_options = [0,1,2,3,4,5]
                                   grass_density = tile_info.get("grass_density", 0)
                                   grass_density = round(random.gauss(45, 8))
                                   
                                   self.grass_manager.place_tile(location=(col_index, row_index), density=grass_density, grass_options=grass_options)
                                   self.grass_tile_grid[row_index][col_index] = True
                               
                                elif tile_info.get("type") == "grass_big":
                                   
                                   grass_options = tile_info.get("grass_options", [6,7,8,9,10,11])
                                   grass_options = [6,7,8,9,10,11]
                                   grass_density = tile_info.get("grass_density", 0)
                                   grass_density = round(random.gauss(20, 6))
                                   
                                   self.grass_manager.place_tile(location=(col_index, row_index), density=grass_density, grass_options=grass_options)
                                   self.grass_tile_grid[row_index][col_index] = True
                                
                               
                                
                                else:
                                    # Create normal tiles
                                    new_tile = Tile(pos, [self.ground_sprites], 'ground', tile_image, valid_interaction_types)
                                    
                                    tile_grid[row_index][col_index] = new_tile
                                    self.tile_map[(pos[0], pos[1])] = new_tile  # Retain the mapping for all tiles
                    
                # Assign neighbors to WaterTiles after all tiles are instantiated
                for y in range(len(layout_csv)):
                    for x in range(len(layout_csv[0])):
                        if isinstance(water_tile_grid[y][x], WaterTile):
                            neighbors = {
                                'left': water_tile_grid[y][x - 1] if x > 0 and isinstance(water_tile_grid[y][x - 1], WaterTile) else None,
                                'right': water_tile_grid[y][x + 1] if x < len(water_tile_grid[0]) - 1 and isinstance(water_tile_grid[y][x + 1], WaterTile) else None,
                                'top': water_tile_grid[y - 1][x] if y > 0 and isinstance(water_tile_grid[y - 1][x], WaterTile) else None,
                                'bottom': water_tile_grid[y + 1][x] if y < len(water_tile_grid) - 1 and isinstance(water_tile_grid[y + 1][x], WaterTile) else None
                            }
                            water_tile_grid[y][x].adjacent_tiles = neighbors  # Update the WaterTile's neighbors
            
    
                self.visible_sprites.set_grass_grid(self.grass_tile_grid)


       
class Level4:
    def __init__(self, input_manager,selected_player_info_dir, layouts_dir, player_stats ):

        self.start_map(input_manager = input_manager,
                       selected_player_info_dir = selected_player_info_dir,
                       layouts_dir = layouts_dir,
                       player_stats = player_stats )


    def start_map(self,
                  input_manager,
                  selected_player_info_dir,
                  layouts_dir,
                  player_stats=None,
                  display_surface = None,
                  layout_manager= None,
                  Player = None,
                  restart = False,
                  player_position = None):
        
        self.player_base_stats = player_stats
        ## callback methods these do not actually need to be in init i think, just seems lgocial.
        self.persistent_enemy_data = {}
        standard_items_path = '../Graphics/Standard_Items/standard_items.json'
        self.item_spawner = ItemSpawner()
        self.item_spawner.load_item_mapping(standard_items_path)
        self.particle_dict = {}
        
        self.last_trigger_time = None
        self.trigger_cooldown = 5000  # 1 second cooldown
        
        if display_surface:
            # Set old display surface : maybe this is the problem actually, maybe killing the sprites kills the surface or something
            #print("set display surface from previous level")
            self.display_surface = display_surface
        else:
            self.display_surface = pygame.display.get_surface()  # This returns None Maybe i need to do what ever else is done before this
                                                                 # like what ever is in Main.py.... this is so backwards.        
            # Set up a new display surface with transparency
            self.display_surface = pygame.display.set_mode(self.display_surface.get_size(), pygame.SRCALPHA)

        
        self.weather_overlay = WeatherOverlay(self.display_surface)
        self.game_paused = False
        self.upgrade_menu_open = False
        self.inventory_open = False
        self.attack_selection_open = False 
        self.player_config_open = False
        self.selected_player_info_dir = selected_player_info_dir
        self.layouts_dir = layouts_dir
        self.input_manager = input_manager
        self.input_manager.reset()
        self.current_layout = None
        self.layouts_dir = layouts_dir
        self.ui=UI()
        with open(f"{layouts_dir}/initial_layout_name.txt", "r") as file:
            initial_layout_dir = file.read().strip()
        print(f"layout dir  : {layouts_dir}")
        try:
            with open(f"{layouts_dir}/layout_general_config.txt", "r") as file:
                layout_general_config = file.read().strip()   # for now just indicates daylight, need to develop this .json format and files
        except:
            layout_general_config = "True"
        #print(f"resulting layout general config : {layout_general_config}")
        #print(type(layout_general_config))
        layout_general_config = layout_general_config.strip()
        self.daytime_layout  = layout_general_config != "False" # indicates whether we use the daytime overlay, really this should be a part of the general brightness overlay ? 
        #print(f"resulting daytime layount in level start map method : {self.daytime_layout}")
        self.wind_timer = 0
        self.wind_interval = 2000
        
        #print( initial_layout_dir )
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.enemy_attack_sprites = pygame.sprite.Group()


        if layout_manager :
            #print("layout was passed to the restart")
            self.layout_manager = layout_manager
            
        else:
            # Initialize LayoutManager with callbacks
            self.layout_manager = LayoutManager(
                selected_player_info_dir, 
                TILESIZE, 
                restore_persistent_enemies_callback=self.restore_persistent_enemies,
                initialize_map_items_callback=self.initialize_map_items  # Pass the method reference directly
                
                )        

# After player initialization in Level4
        self.spawner = Spawner( self, self.persistent_enemy_data,self.fire_projectile )
        self.layout_manager.set_spawner( self.spawner, self.layout_manager.add_obstacle_sprite_to_quad_tree )
        
        
        #print("JUST SET DISPLAY SCREEN ")
        #print(self.display_surface)
        #if display_surface:
            #print(display_surface)
        #else:print("None")
        
        if not restart :         
            self.layout_manager.daytime_brightness_overlay.set_display_surface(self.display_surface)
            self.layout_manager.initialize_layout( initial_layout_dir ) # Convention: initial layout is defined by naming convention       
        
        self.current_layout = initial_layout_dir

      
        #self.add_item_to_level_callback = add_item_to_level # random af not sure what this was used for .
        
        
        if not Player:
            # Instantiate the player here
            self.player = SpecificPlayer(
                self.selected_player_info_dir,
                (15 * TILESIZE, 25 * TILESIZE),
                [self.layout_manager.visible_sprites],  # Pass the visible_sprites from LayoutManager
                self.layout_manager,  # Pass the obstacle_sprites from LayoutManager
                self.create_attack,
                self.destroy_attack,
                self.create_magic,
                self.create_evasion,
                self.player_base_stats,
                self,
                self.input_manager,
                self.layout_manager.obstacle_quad_tree,
                self.layout_manager.entity_quad_tree,
                layout_callback_update_quad_tree = self.layout_manager.add_obstacle_sprite_to_quad_tree  ## TODO : rename this, its for entities, obstacles are done in the init only.
            )
           
            # Pass the player to the LayoutManager for interaction handling
            self.layout_manager.set_player(self.player)
        
        
        self.layout_manager.set_player(self.player)
        self.weather = Weather()
        
        
        self.upgrade = Upgrade(self.player, self.input_manager)
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        self.evasion_player = EvasionPlayer(self.animation_player, self.create_trap)
        self.current_attack = None

        if restart:
            #print(f"Player position being set to {player_position} in start_map")
            self.player.rect.topleft = player_position
            self.player.hitbox.topleft = player_position
            #print(self.player.rect.center)
            self.player.update(layout_switch = False,
                               QuadTree=self.layout_manager.obstacle_quad_tree,
                               entity_quad_tree= self.layout_manager.entity_quad_tree)
            
            # # why am i updating here twice  ? 
            # for sprite in self.layout_manager.visible_sprites:
            #     if hasattr(sprite, 'type'):
            #         if sprite.type == 'player':
            #             sprite.update()
            #print("pre")
            self.layout_manager.obstacle_quad_tree.print_all()
            #print(f"Player position as in start map func : {player_position}")
            
            
            
            
            ###### One solution is to just get the value of whether the destination place should have daytime layout again and set it true/false.
            
            
            
            #print(f'JUST BEFORE LAST INITIALIZE LAYOUT DAYTIME VALUE : {self.daytime_layout}')
            
            
            self.layout_manager.initialize_layout( self.layouts_dir,
                                                  player_position=player_position,# Im doing something shitty here.# just need to remove, the position is actually set in this method. 
                                                  restart = True,
                                                  Player = self.player, ## unecesary, we can set player from level with the set player method.
                                                  daytime_layout = self.daytime_layout,
                                                  prepared_daytimeoverlay = None #self.layout_manager.daytime_brightness_overlay # so silly i set it above
                                                  )
            
            if self.layout_manager.daytime_brightness_overlay:
                self.layout_manager.daytime_brightness_overlay.set_display_surface(self.display_surface) # TODO: done separately in both restart and not restart....terrible
        
           # print("post")
            self.layout_manager.obstacle_quad_tree.print_all()

    #def initialize_map_items(self, layout_path):
    #    initial_items_path = os.path.join(layout_path, 'initial_map_items.json')
    #    items_info = self.item_spawner.spawn_fixed_items(initial_items_path)
    #    self.layout_manager.place_items_on_map(items_info)
    def check_trap_triggers(self, trap):
        # Use circle-based collision detection to determine if enemies are within the trap's radius
        enemies_in_range = pygame.sprite.spritecollide(trap, self.layout_manager.spawner.enemies, False, pygame.sprite.collide_circle)
        return enemies_in_range
    # def check_trap_triggers(self,trap):
    #      enemies_in_range =  [enemy for enemy in self.layout_manager.spawner.enemies if trap.rect.colliderect(enemy.rect.inflate(trap.radius, trap.radius))]
    #      return enemies_in_range
    def create_trap(self, trap_config):
        """Method to create a trap using the spawner."""
        return self.layout_manager.spawner.spawn_trap(trap_config)
    ##@profile
    def get_tile_valid_actions(self, position, only_tile_below = True):
        """
        Determines the type of tile at the given position.
        
        :param position: A tuple (x, y) representing the position to check.
        :return: A string representing the tile type, or None if not found.
        """
        #print(f"tile below :{only_tile_below}")
        #print(f"position: {position}")
        if not only_tile_below:
            tiles = {}
            tiles.update( {'on':self.layout_manager.tile_map.get(position)} )
            position = (position[0] + TILESIZE, position[1])
            tiles.update( {'right':self.layout_manager.tile_map.get(position)} )
            position = (position[0] - 2*TILESIZE, position[1])
            tiles.update( {'left':self.layout_manager.tile_map.get(position)} )
            position = (position[0], position[1] + TILESIZE)
            tiles.update( {'below':self.layout_manager.tile_map.get(position)} )
            position = (position[0], position[1] - 2*TILESIZE)
            tiles.update( {'above':self.layout_manager.tile_map.get(position)} )
            
            #print(f"TILES: {tiles}")
        else:
            tiles = {'on':self.layout_manager.tile_map.get(position)}
        #print(f"identified tile : {tile} at position :{position}") # valid_I_T:{tile.valid_interaction_types}")
        #print(self.layout_manager.tile_map)
        possible_interaction_types = tiles
        possible_interaction_types_set = set()
        for place in tiles.keys():
            
            if tiles[place]:
                interaction_types = tiles[place].valid_interaction_types
                possible_interaction_types[place] = interaction_types
                
                for interaction_type in interaction_types:
                    possible_interaction_types_set.add(interaction_type)
            
        if len(possible_interaction_types_set) > 0:
            #print(possible_interaction_types)
            #print(possible_interaction_types_set)
            return [possible_interaction_types,possible_interaction_types_set]  # Assuming each Tile has a 'tile_type' attribute
        return None


    def initialize_map_items(self, item_config_path):
        """Initialize map items from configuration."""
        self.item_spawner.load_item_config(item_config_path)
        items = self.item_spawner.spawn_fixed_items()
        #print(dir(items[0]))
        for item in items:
            item.pos[0] = item.pos[0]*TILESIZE # size defined in grid squares.
            item.pos[1] = item.pos[1]*TILESIZE

            # Change required to scale position here.
            item_instance = Item(item.image_path, item.pos, item.item_id, item.effect, item.effect_type)  # Create a new item instance for each position
            self.layout_manager.add_item_visual(item_instance)



    def get_level_up_threshold(self, level):
        return 1000 * level ** 2

    def check_level_up(self):
        threshold = self.get_level_up_threshold(self.player.power_level)
        if self.player.exp >= threshold:
            self.player.power_level += 1
            self.player.exp = 0  # Reset experience
            # Increase player stats here, if desired
            self.trigger_level_up_effect()
            self.player.player_config.add_remaining_points(20)
            self.toggle_player_config()


    def trigger_level_up_effect(self):
        # Example using an existing animation player
        # You might need to adjust the path and animation specifics
        animation_frames = import_folder('../Graphics/LevelUpAnimation')
        animation_position = self.player.rect.center 
        animation_speed = 30 
        self.layout_manager.trigger_animation(animation_frames, animation_position, animation_speed)


    def restore_persistent_enemies(self,layout_path):
        if layout_path in self.persistent_enemy_data:
            for enemy_state in self.persistent_enemy_data[layout_path]:
                self.spawner.restore_enemy(enemy_state)



    def handle_item_collection(self):
        """Check for collisions between the player and items to handle item collection."""
        for visual_item in [sprite for sprite in self.layout_manager.visible_sprites if isinstance(sprite, ItemVisual)]:
            if self.player.rect.colliderect(visual_item.rect):
                self.player.pickup_item(visual_item.item)  # Pass the logical item to the pickup method
                self.item_spawner.remove_item( visual_item.item )  
                visual_item.kill()

    def check_enemy_deaths(self):
        dead_enemies = [enemy for enemy in self.spawner.enemies if enemy.is_dead()]
        
        #print("dead_enemies")
        #print(len(dead_enemies))
        
        processed_enemies = [] 
        #print(f"DEAD ENEMIES : {dead_enemies}")
        for enemy in dead_enemies:
            dropped_items = self.item_spawner.drop_from_enemy(enemy)
            #print(dropped_item_info)
            if dropped_items:
                # Convert the item drop position to map coordinates if necessary
                drop_position = (enemy.rect.x, enemy.rect.y)
                #self.layout_manager.place_items_on_map([dropped_item_info]) # Place items on map not used
     
                #print(f"ITEMS OUTPUTTED BY SPAWNER - DROPPED  ITEMS: {dropped_items}")
                pos_offset_counter = 0
                
                for item in dropped_items:
                    #item.pos[0][0] = drop_position[0] + pos_offset_counter*random.randint(12,40)
                    #item.pos[0][1] = drop_position[1] + pos_offset_counter*random.randint(12,40)
                    self.layout_manager.add_item_visual(item)
                    pos_offset_counter += 1

            processed_enemies.append(enemy)
        # Remove processed enemies from the list of enemies managed by the spawner
        #print("processed enemies")
        #print(len(processed_enemies))
        #print("number enemies in spawner")
        #print(len(self.spawner.enemies))
        for enemy in processed_enemies:
            self.spawner.enemies.remove(enemy)
        #print("number enemies in spawner")
        #print(len(self.spawner.enemies))

    def save_enemy_states(self):
        # Save the state of all persistent enemies
        self.persistent_enemy_data[self.current_layout] = [
            {
                'type': enemy.type,
                'position': enemy.rect.topleft,
                'health': enemy.health
            }
            for enemy in self.spawner.enemies if enemy.persistent
        ]


    def check_triggers(self):
        
        current_time = pygame.time.get_ticks()
        if self.last_trigger_time is not None and current_time - self.last_trigger_time < self.trigger_cooldown:
            return  # Still in cooldown period, do not activate triggers

        for trigger in self.layout_manager.trigger_sprites:
            if self.player.rect.colliderect(trigger.rect):
                new_player_position = trigger.new_player_position

                #print("new position")
                #print(new_player_position)
                #print(new_player_position[0])
                #print(new_player_position[1])
                #print(" new version ")
                #print([pos * TILESIZE for pos in new_player_position])


                new_player_position[0] = new_player_position[0]*TILESIZE
                new_player_position[1] = new_player_position[1]*TILESIZE

                #print("old version")
                #print( new_player_position )
                 # Reset InputManager state
                self.input_manager.reset()
                self.last_trigger_time = current_time
                #print(f"trigger path : {trigger.destination_layout}")
                #print(f" new player position : {trigger.new_player_position}")
                
                
           
                
                
                
                self.start_map(input_manager = self.input_manager,
                               selected_player_info_dir = self.selected_player_info_dir,
                               layouts_dir = trigger.destination_layout,
                               display_surface=self.display_surface,
                               layout_manager=self.layout_manager,
                               Player = self.player,
                               restart = True,
                               player_position = new_player_position)
                
                ## So , the issue seems to be that i run level.run in main, in level.run, i check triggers, but this stops the game_loop,
                #       although, i does not, i guess as expected, what is does is is keep going but have display_surfce = None.
                
                
                #self.layout_manager.spawner.restore_persistent_enemies(trigger.destination_layout) # Done with callback.
                
                

    def save_enemy_states(self, current_layout):
        self.persistent_enemy_data[current_layout] = [{'type': enemy.type, 'position': enemy.rect.topleft, 'health': enemy.health} for enemy in self.spawner.enemies if enemy.persistent]




    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.layout_manager.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        #print("Magic cost")
        #print(cost)
        # Magic creation logic here
        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, [self.layout_manager.visible_sprites])
        elif style == "flame":
            self.magic_player.flame(self.player, cost, [self.layout_manager.visible_sprites, self.attack_sprites])
        if style == 'ice_ball':
            particle = self.magic_player.ice_ball2(self.player, cost, [self.layout_manager.visible_sprites, self.attack_sprites], self.layout_manager.entity_quad_tree)
            # Register particle in the dictionary
            self.particle_dict[id(particle)] = particle
       
        
    def redirect_projectile_callback(self, projectile_id, new_direction):
        projectile = self.particle_dict.get(projectile_id)
        if projectile:
            projectile.movement = new_direction * projectile.movement.length()
            projectile.distance_moved = 0
            # Add the particle to the enemy_attack_sprites group
            if not projectile.groups().__contains__(self.enemy_attack_sprites):
                self.enemy_attack_sprites.add(projectile)
            
                    
                
     
    def create_evasion(self, style, direction):
        # Callback to handle particle creation on each movement step
        # def handle_slide_particles(player):
        #     current_tile_center = (
        #         (player.rect.centerx // TILESIZE) * TILESIZE + TILESIZE // 2,
        #         (player.rect.centery // TILESIZE) * TILESIZE + TILESIZE // 2
        #     )
        #     self.animation_player.create_particles("slide_effect", current_tile_center, self.player.groups())
            
        # Initiate the slide with the particle handling callback
        if style == 'slide':
            self.evasion_player.slide(self.player, direction)#, handle_slide_particles)
        if style == 'create_ice_clone':
            self.evasion_player.create_ice_clone( self.player, effect_type='freeze' , radius = 5)# TODO radiu should be a player attribute right ? player.evasion attribute 

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):

        
        # TODO : implement quadtree ? its not particularly heavy part of the code...
        #      : implement mask collision
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        # Assuming 'physical' or 'magic' as example attack types
                        attack_type = 'physical' if attack_sprite.sprite_type == 'weapon' else 'magic'
                        target_sprite.get_damage(self.player, attack_type)


    
    def enemy_projectile_logic(self):

        if self.enemy_attack_sprites:
            #print("ATTACK SPRITES EXIST")
            for enemy_attack_sprite in self.enemy_attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(enemy_attack_sprite, [self.player], False)# TODO eventually they should be able to damage all friendly stuff.
                if collision_sprites:
                    #print("COLISION NOTICED !!!!!!!!!!!")
                    for target_sprite in collision_sprites:
                        # TODO : define particle effect with damage amount, 
                        # also get target resistance etc.
                        self.damage_player(amount = 10, attack_type = None)


  

    def damage_player(self, amount, attack_type=None):
        
        
        #print(f"made it to damage player , vulerable: {self.player.vulnerable}")
        #print(amount)
        
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            
            if attack_type:
                if attack_type != 'melee': ## TODO : a at the moment this is recieving attack type to do attack particles, 
                                                    # we do not have any attack particles for this so screw it.
                                                    
                    self.animation_player.create_particles(attack_type, self.player.rect.center, [self.layout_manager.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        # Particle effect logic here
        self.animation_player.create_particles(particle_type, pos, [self.layout_manager.visible_sprites])

    def add_exp(self, amount):
        self.player.exp += amount
        self.check_level_up()


    def toggle_menu(self):
        self.game_paused = not self.game_paused
        self.upgrade_menu_open = not self.upgrade_menu_open

    def toggle_inventory(self):
        self.game_paused = not self.game_paused
        self.inventory_open = not self.inventory_open
        self.player.inventory.visible = self.inventory_open

    def toggle_attack_selection(self):
        self.game_paused = not self.game_paused
        self.attack_selection_open = not self.attack_selection_open
        self.player.attack_selection.visible = self.attack_selection_open
        
    
    def toggle_player_config(self):
        self.game_paused = not self.game_paused
        self.player_config_open = not self.player_config_open
        self.player.player_config.visible = self.attack_selection_open # Dont think this is even being used.
        
    def update_player_stats(self): # TODO: bit messy in terms of calling player from level,,, i do interaction issues in level often but 
                                   # really this can be a player method, the only this is that the player config screen recieves level
                                   # so we call it from level as opposed to level.player....
        new_stats = self.player.player_config.final_stats 
        self.player.stats = new_stats
        
        # Define a method to get the direction vector from an angle
    def get_direction_from_angle(self, angle):
        # Convert angle to radians
        radians = math.radians(angle)
        # Calculate the x and y components of the direction vector
        direction_x = math.cos(radians)
        direction_y = -math.sin(radians)  # Negative sin because y-coordinates are flipped in pygame
        # Return the direction vector
        return pygame.math.Vector2(direction_x, direction_y)
    #@profile
    def fire_projectile(self, enemy_pos, target_pos, projectile_type, groups): ### groups not actually used, we pass level references to the groups explicitely below , regardles,, this could be confusing ISSUE
    
        # Calculate the angle to the target
        angle_to_target = self.calculate_angle(enemy_pos, target_pos)
        # Round the angle to the nearest multiple of 20 degrees
        rounded_angle = self.round_angle(angle_to_target)
        # Determine the direction vector based on the rounded angle
        direction = self.get_direction_from_angle(rounded_angle)
        # Invoke the method responsible for creating the projectile, passing in the direction
        self.animation_player.create_particles(animation_type = projectile_type,
                                               pos = enemy_pos,
                                               groups = [self.enemy_attack_sprites, 
                                                         self.layout_manager.visible_sprites],
                                               quadtree=self.layout_manager.entity_quad_tree,
                                               direction=direction*12,# TODO :actually controls speed, i need to unify how i do it in magic and here, two similar params
                                               is_moving = True,
                                               total_distance=1000
                                               )


    def calculate_angle(self, source, target):
        dx = target[0] - source[0]
        dy = target[1] - source[1]
        return math.degrees(math.atan2(-dy, dx)) % 360  # Calculate angle in degrees

    # Define a method to round the angle to the nearest multiple of 20 degrees
    def round_angle(self, angle):
        return round(angle / 20) * 20  # Round to the nearest multiple of 20 degrees



    #@profile
    def run(self,dt):
        
        #clock = pygame.time.Clock()  
        #dt = clock.tick(60) / 1000 # the 120 is arbitrariy bigger than the actual fps of 60 we noticed that using 60 it thinks we are overclocking for some reason and introduces a delay taking us to 40 fps  
        #clock.tick(FPS)
        #dt = 0.001
        ##### IM NOT SURE WHERE OR HOW BUT EVERYTHING DEPENDING ON DT GOES SUPER FAST I DNO IF I MULTIPLY IT OR SUMIN , I NEED TO INVESTIGATE
        ##### BUT ATM I JUST SLOW IT DOWN LIKE THIS 
        #print(dt)
        dt_real = dt   # dno what the dt divided by fps is .... some wierd desperate attempt to make something work..
        dt = dt / FPS
        self.wind_timer += dt
        self.display_surface.fill((0, 0, 0)) 
        #print(FPS)
     
        #print(self.player.rect.center)
         
        self.check_triggers() # i guess i need to pass persist data ?  
        #print(self.player.rect.center)
        #print(self.layout_manager.player.rect.center)
        self.layout_manager.spawner.on_layout_update()
        #print(f"\n\n after layout update {self.player.rect.x}\n\n")
        #self.layout_manager.visible_sprites.custom_draw(self.player,dt, self.weather.weather_intensity, self.weather.light_level)
       #print(f"\n\n after after custom draw {self.player.rect.x}\n\n")
        
        

        if self.game_paused:
            if self.upgrade_menu_open:
                self.upgrade.display()
            elif self.inventory_open:
                self.player.inventory.display(self.display_surface)
                self.player.inventory.input()
            elif self.attack_selection_open:
                self.player.attack_selection.display(self.display_surface)
                self.player.attack_selection.input()
                self.player.update_derived_attributes()
            elif self.player_config_open:
                
                self.player.player_config.draw(self.display_surface) # TODO: align naming convensions of these screens.
                self.player.player_config.handle_events(self)
                #self.player.stats = self.player.player_config.final_stats
                
        else:
            
            
            if self.layout_manager.daytime_layout:
                self.layout_manager.visible_sprites.custom_draw(self.player,dt, self.weather.weather_intensity, self.weather.light_level)
                self.weather.update(dt)
                self.weather_overlay.set_weather(self.weather.weather_type,
                                                 self.weather.weather_intensity,
                                                 self.weather.wind_direction)
                self.layout_manager.daytime_brightness_overlay.set_time_of_day( self.weather.current_time )
                self.layout_manager.daytime_brightness_overlay.draw()
                if self.weather.weather_type != 'clear':
                    self.weather_overlay.update(dt) 
                    self.weather_overlay.draw()
                
                wind_force = self.weather.calculate_wind_force()
                
                        
                self.brightness_radius = 220
                center_x = self.display_surface.get_width() // 2
                center_y = self.display_surface.get_height() // 2
                num_circles = 6  # Adjust as needed
                if (self.weather.current_time > 18 and self.weather.current_time <= 20)  or (self.weather.current_time <= 10 and self.weather.current_time > 9) :
                    brightness_factor = 0.008
                if (self.weather.current_time > 20 and self.weather.current_time <= 22)  or (self.weather.current_time <= 9 and self.weather.current_time > 7) :
                    brightness_factor = 0.009
                elif self.weather.current_time > 22 or self.weather.current_time <= 10 :
                    brightness_factor = 0.012
                else: brightness_factor = 0.007
                
                # Create a surface for the brightness effect
                brightness_surface = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
                
                # Draw concentric circles with decreasing brightness
                for i in range(num_circles):
                    if i >= 5: continue
                    #radius = self.brightness_radius - ( self.brightness_radius / num_circles )*i  # Adjust the increment as needed
                    radius = self.brightness_radius * (1/((i+1)**0.70))
                    brightness = 255  # Adjust the decrement as needed
                    if i == 0 :brightness_factor_temp = brightness_factor
                    else: brightness_factor_temp = brightness_factor_temp*1.58
                            
                    # Draw the circle with the calculated alpha value
                    pygame.draw.circle(brightness_surface, (255 * brightness_factor_temp, 255 * brightness_factor_temp, 255 * brightness_factor_temp, 255 * brightness_factor_temp), (center_x, center_y), radius)
                
                    # Blit the brightness surface onto the display surface with additive blending
                    self.display_surface.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
                
            # Iterate over each grass tile and apply the wind force
            #print(f"wind_force :{wind_force}")
            
                    
        
                self.layout_manager.visible_sprites.update_parallel( obstruction_quad_tree = self.layout_manager.obstacle_quad_tree,
                                                                     entity_quad_tree = self.layout_manager.entity_quad_tree,
                                                                     dt=dt,
                                                                     weather = self.weather, 
                                                                     wind_force=wind_force )
                    
                
                #print("new quad tree item mappings:")
                #print(self.layout_manager.entity_quad_tree.manager.item_mapping)
            else:
                #print("new quad tree item mappings:")
                #print(self.layout_manager.entity_quad_tree.manager.item_mapping)
                self.layout_manager.visible_sprites.update_parallel( obstruction_quad_tree = self.layout_manager.obstacle_quad_tree,
                                                                     entity_quad_tree = self.layout_manager.entity_quad_tree,
                                                                     dt=dt,
                                                                     weather = None,
                                                                     wind_force = None )
                
                self.layout_manager.visible_sprites.custom_draw(self.player,dt, 0, 0.5) # default weather intensity and light level (should be atleast an attribute of the layout manager, really contained in the weather manager.)
            #self.layout_manager.update_weather(self.weather)
            
            self.layout_manager.spawner.handle_spawn_areas( self.player,dt_real )        
            # Check for and update enemy sprites specifically
            self.ui.display(self.player)

            for sprite in self.layout_manager.visible_sprites.sprites():
                # debug
                # if hasattr(sprite, 'frozen'):
                #     if hasattr(sprite, 'frozen_image'):
                #         pygame.display.get_surface().blit(sprite.frozen_image, (100, 100))


                if hasattr(sprite, 'enemy_update'):
                    sprite.enemy_update(self.player,self.layout_manager.entity_quad_tree)
                elif isinstance( sprite, Trap):
                    enemies_in_range = self.check_trap_triggers(sprite)
                    # Prolly pass  enemies to activate to freeze them n that.
                    if len(enemies_in_range) > 0:
                        sprite.activate()
                       
             
            spawned_items = self.item_spawner.update()

            #print(f"In level game loop, spawned items from item spawner update : {spawned_items}")

            for item in spawned_items:
                #print(f"\n\nATTEMPTING TO SPAWN FISH \n\n item:{item}\n id:{item.item_id}\n pos:{item.pos}")
                self.layout_manager.add_item_visual(item)            
            
            self.check_enemy_deaths()
            self.handle_item_collection()
            #self.layout_manager.visible_sprites.enemy_update(self.player)  
           #print(f"\n\n after PRE ATTACK {self.player.rect.x}\n\n")
            self.player_attack_logic()
            self.enemy_projectile_logic()
           #print(f"\n\n after POST ATTACK {self.player.rect.x}\n\n")
            self.save_enemy_states(self.current_layout) #mkght be a big inefficiency 
           
            
            self.layout_manager.display_time(self.display_surface)

           #print(f"\n\n after END OF LOOP {self.player.rect.x}\n\n")
            #Now draw the weather overlay



        #
    
        # Grass  !

        ## Apply current wind force every certain time

        # if self.wind_timer >= self.wind_interval:
        #     wind_force = self.weather.calculate_wind_force()
        #     for row_index, row in enumerate(self.layout_manager.grass_tile_grid):
        #         for col_index, val in enumerate(row):
        #             if val:
        #                 tile_position = (col_index, row_index)
        #                 self.layout_manager.grass_manager.apply_force(tile_position, wind_force[0], wind_force[1])
        #     self.wind_timer = 0  # Reset the timer after applying force

        # # Finally, render the grass tiles
        # for row_index, row in enumerate(self.layout_manager.grass_tile_grid):
        #     for col_index, val in enumerate(row):
        #         if val:
        #             self.layout_manager.grass_manager.update_render(self.display_surface, dt)
    
 
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, ground_sprites, grass_manager,overhead_areas):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.window_width, self.window_height = self.display_surface.get_size()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
                
                # Define the dimensions for the grass surface
        grass_width = self.display_surface.get_width() - (2 * TILESIZE)
        grass_height = self.display_surface.get_height() - (2 * TILESIZE)
        
        # Set up the grass surface as a subsurface of the display surface
        self.grass_surface = self.display_surface.subsurface( (TILESIZE, TILESIZE, grass_width, grass_height) )
        
        self.grass_half_width = self.grass_surface.get_width() // 2
        self.grass_half_height = self.grass_surface.get_height() // 2
        
        
        self.offset = pygame.math.Vector2()
        self.grass_offset = pygame.math.Vector2()
        self.ground_sprites = ground_sprites
        self.ground_surface = None
        self.create_ground_surface()
        self.grass_manager = grass_manager
        self.update_grass_with_wind_frequency = 5000
        self.wind_last_affected_grass = 0
        self.t=0 # forgrass rotaryfunctin, name it better.
        
        # Threading.
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = Lock()
        
        self.overhead_areas = overhead_areas

    #@profile
    def update_parallel_inview(self, dt=None, weather=None, wind_force=(0, 0), num_threads=8, *args, **kwargs):
        #print("attempted parallel update")
        sprites_in_view = self.get_sprites_in_view()
        sprite_batches = [sprites_in_view[i::num_threads] for i in range(num_threads)]
        futures = []

        for batch in sprite_batches:
            future = self.executor.submit(self.update_for_parallel, batch, dt, self.lock)
            futures.append(future)

        updated_sprites = []
        for future in futures:
            updated_sprites.extend(future.result())

        # Extend with non-visible sprites
        updated_sprites.extend(sprite for sprite in self.sprites() if sprite not in updated_sprites)

        # Update self.sprites with the updated sprites
        self.sprites().clear()
        self.sprites().extend(updated_sprites)
        

    #@profile
    def update_parallel(self, obstruction_quad_tree,entity_quad_tree, dt=None, weather=None, wind_force=(0, 0), num_threads=1, *args, **kwargs):
        #print("attempted parallel update")
        #sprites_in_view = self.get_sprites_in_view()
        sprite_batches = [self.sprites()[i::num_threads] for i in range(num_threads)]
        futures = []

        for batch in sprite_batches:
            future = self.executor.submit(self.update_for_parallel,obstruction_quad_tree,
                                          entity_quad_tree,
                                          batch,
                                          dt,
                                          self.lock)
            futures.append(future)

        updated_sprites = []
        for future in futures:
            updated_sprites.extend(future.result())

        # Extend with non-visible sprites
        #updated_sprites.extend(sprite for sprite in self.sprites() if sprite not in updated_sprites)

        # Update self.sprites with the updated sprites
        self.sprites().clear()
        self.sprites().extend(updated_sprites)

    def set_grass_render_window_size_with_timeofday(self,light_level):
        #print("light_level!")
        #print(light_level)
        if light_level <= 1 and light_level > 0.75:
                # Define the dimensions for the grass surface
            grass_width = self.display_surface.get_width() - (2 * TILESIZE)
            grass_height = self.display_surface.get_height() - (2 * TILESIZE)
            
            # Set up the grass surface as a subsurface of the display surface
            self.grass_surface = self.display_surface.subsurface( (TILESIZE, TILESIZE, grass_width, grass_height) )
            
            self.grass_half_width = self.grass_surface.get_width() // 2
            self.grass_half_height = self.grass_surface.get_height() // 2

        # if light_level <= 0.75 and light_level > 0.5:
        #         # Define the dimensions for the grass surface
        #     grass_width = self.display_surface.get_width() - (2.5 * TILESIZE)
        #     grass_height = self.display_surface.get_height() - (2.5 * TILESIZE)
            
        #     # Set up the grass surface as a subsurface of the display surface
        #     self.grass_surface = self.display_surface.subsurface( (TILESIZE*1.25, TILESIZE*1.25, grass_width, grass_height) )
            
        #     self.grass_half_width = self.grass_surface.get_width() // 2
        #     self.grass_half_height = self.grass_surface.get_height() // 2
            
        #print(light_level)
        if light_level <= 0.5 :
                # Define the dimensions for the grass surface
            grass_width = self.display_surface.get_width() - (3 * TILESIZE)
            grass_height = self.display_surface.get_height() - (3 * TILESIZE)
            
            # Set up the grass surface as a subsurface of the display surface
            self.grass_surface = self.display_surface.subsurface( (TILESIZE*1.5, TILESIZE*1.5, grass_width, grass_height) )
            
            self.grass_half_width = self.grass_surface.get_width() // 2
            self.grass_half_height = self.grass_surface.get_height() // 2
            
        #print(f"RESULTING WIDTH : {self.grass_half_width}")
            

    def set_grass_grid(self,grass_grid):
        self.grass_grid = grass_grid

    def update_tile_on_ground_surface(self, tile):
        if not self.ground_surface:
            self.create_ground_surface()
        else:
            # Redraw only the area of the changed tile
            self.ground_surface.blit(tile.image, tile.rect.move(-self.min_x, -self.min_y))

    def create_ground_surface(self):
        if not self.ground_sprites:
            return
        self.min_x = min(sprite.rect.left for sprite in self.ground_sprites)
        self.max_x = max(sprite.rect.right for sprite in self.ground_sprites)
        self.min_y = min(sprite.rect.top for sprite in self.ground_sprites)
        self.max_y = max(sprite.rect.bottom for sprite in self.ground_sprites)

        width = self.max_x - self.min_x
        height = self.max_y - self.min_y

        self.ground_surface = pygame.Surface((width, height)).convert_alpha()
        self.ground_surface.fill((0, 0, 0, 0))
        for sprite in self.ground_sprites:
            self.ground_surface.blit(sprite.image, sprite.rect.move(-self.min_x, -self.min_y))
    #@profile
    def custom_draw(self, player,dt, wind_intensity, light_intensity):
        
        if self.ground_surface is None:
            self.create_ground_surface()
            
        self.offset.x = player.rect.centerx - self.half_width 
        self.offset.y = player.rect.centery - self.half_height
        self.grass_offset.x = player.rect.centerx - self.grass_half_width 
        self.grass_offset.y = player.rect.centery - self.grass_half_height
        
        
        ground_rect = self.ground_surface.get_rect(topleft=(-self.offset.x, -self.offset.y))
        self.display_surface.blit(self.ground_surface, ground_rect.topleft)
        
        
        self.set_grass_render_window_size_with_timeofday( light_intensity )
            
        #print(f" dt : {self.t}")
        self.t += dt*1500*wind_intensity
        rot_function = lambda x, y: int(math.sin(self.t / 60 + x / 100) * 15)
        
        # if player on grass
        
        self.grass_manager.apply_force( player.rect.center , 25 , 20)
        
        
        #print( self.grass_offset )
        #print( self.offset )
        
        # Draw grass relative to player
        self.grass_manager.update_render(self.grass_surface,
                                         dt, 
                                         offset=(self.grass_offset.x , 
                                                 self.grass_offset.y ),
                                      rot_function=rot_function )
        player_drawn = False
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            #print(sprite)
            #print(dir(sprite))
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            if hasattr(sprite, "monster_name"):
                if sprite.monster_name == 'raccoon':
                    self.grass_manager.apply_force( sprite.rect.center , 110 , 40)
                    
            # if hasattr(sprite, "type") and sprite.type == "player":
            #     player_drawn = True
            #     # Draw overhead areas if the player is within one
        # Draw overhead areas if the player is within one
        #if player_drawn:
        #print("overhead")
        #print(self.overhead_areas)
        for area, image_section in self.overhead_areas:
            #print(f"area : {area}")
            #print(f"player pos : {player.rect.center}")
            if area.colliderect(player.rect):
                self.display_surface.blit(image_section, (area.x - self.offset.x, area.y - self.offset.y))

    

    #@profile
    
    def set_overhead_areas(self, overhead_areas):
        self.overhead_areas = overhead_areas
    
    def update(self, dt=None, weather=None, wind_force=(0, 0), *args, **kwargs):
        
        for sprite in self.sprites():
            if isinstance(sprite, AnimatedEnvironmentSprite):
                sprite.update(weather)
            else:
                sprite.update(dt)
    #@profile
    def update_for_parallel(self,obstacle_quad_tree, entity_quad_tree, batch, dt=None,lock=None, weather=None, wind_force=(0, 0) , *args, **kwargs):
        updated_sprites = []
        for sprite in batch:
            if isinstance(sprite, AnimatedEnvironmentSprite):
                sprite.update(weather)
            elif isinstance(sprite, Entity):
                sprite.update(dt=dt,
                              QuadTree= obstacle_quad_tree,
                              entity_quad_tree = entity_quad_tree)
            else:
                sprite.update(dt=dt)
            
            # Acquire the lock before updating shared resources
            lock.acquire()
            try:
                updated_sprites.append(sprite)
            finally:
                # Always release the lock, even if an exception occurs
                lock.release()
                
        return updated_sprites
                    
    def is_tile_in_view(self, tile_position):
        """
        Check if a tile at the given position is within the visible area.
        
        Args:
            tile_position (tuple): Position of the tile (x, y).
    
        Returns:
            bool: True if the tile is within the visible area, False otherwise.
        """
        tile_x, tile_y = tile_position
        tile_size = TILESIZE  # Adjust this based on your tile size
        screen_width, screen_height = self.display_surface.get_size()
        screen_left = self.offset.x
        screen_right = self.offset.x + screen_width
        screen_top = self.offset.y
        screen_bottom = self.offset.y + screen_height
        
        # Calculate the bounding box of the tile
        tile_left = tile_x
        tile_right = tile_x + tile_size
        tile_top = tile_y
        tile_bottom = tile_y + tile_size
        
        # Check if any part of the tile is within the visible area
        return (tile_left < screen_right and tile_right > screen_left and
                tile_top < screen_bottom and tile_bottom > screen_top)

    def get_sprites_in_view(self):
        # Determine the visible area based on the player's position and the game window size
        visible_rect = pygame.Rect(self.offset.x, self.offset.y, self.window_width, self.window_height)
        
        # Filter out sprites that are outside the visible area
        visible_sprites = [sprite for sprite in self.sprites() if visible_rect.colliderect(sprite.rect)]
        
        return visible_sprites
                
                
        #### I need to not iterate over the entire grid for this maybe ? still its taking 95% in 
        # the grass method so ... i guess not.
                
        
        
        
        
        ## Ideas to test : have constant force applied to single place to check what it does
        #                  only apply forced to tiles in view.
        
        
    # Pass wind force to the grass manager
 
             

class YSortCameraGroup_old(pygame.sprite.Group):
    def __init__(self,ground_sprites): # Ground sprites in this version because it defines the ground with tiles ( ground_sprites ) 
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.ground_sprites = ground_sprites

#        self.floor_surf = pygame.image.load("../Graphics/Tilemap/Ground.png").convert()
#        self.floor_rect = self.floor_surf.get_rect(topleft = (0, 0))
    ###@profile #decorator to be used for profiling with line_profile, must run Main like this : kernprof -l -v Main2.py
    def custom_draw_withearthquakeeffect(self, player):
        
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Draw ground tiles with slight offset and blending
        for sprite in sorted(self.ground_sprites, key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            # Slightly offset tile position
            offset_pos += pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            # Draw tile
            self.display_surface.blit(sprite.image, offset_pos)
            # Draw semi-transparent overlay on tile edges for blending
            overlay = pygame.Surface((sprite.rect.width, sprite.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 255, 255, 128), overlay.get_rect(), 1)
            self.display_surface.blit(overlay, offset_pos)

        # Draw other sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)



    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

  # Draw ground tiles first
        for sprite in sorted(self.ground_sprites, key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)



    def update(self,dt = None, *args, **kwargs):
        # Update all sprites, passing the player as an argument to those that need it
        for sprite in self.sprites():

            # JUST A POTENTIAL EFFICIENCY IMPROVEMENT TO ONLY PASS PLAYER TO NECESSARY UPDATES ? NO, ITS JUST IF I MAKE THE ENEMY_UPDATE AND REGULAR SPRITE.update method the  same...
            # Pretty sure it was jst a bad idea, but there it is.

            #if hasattr(sprite, 'update_with_player') and sprite.update_with_players:
                #sprite.update(self, player)  # Custom method for sprites needing the player
            #else:
            if isinstance(sprite, Eskimo):
                #print(f"SPRITE BEFORE UPDATE : {sprite}")
                sprite.update(dt)
                #print(f"SPRITE AFTER UPDATE : {sprite}")
            else:
                sprite.update(*args, **kwargs)

