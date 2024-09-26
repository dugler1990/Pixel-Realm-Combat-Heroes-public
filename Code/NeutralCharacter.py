import pygame
import random
from Settings import TILESIZE

from Entity import Entity
class NeutralCharacter(Entity):
    def __init__(self, pos,
                 groups,
                 obstacle_sprites,
                 get_tile_valid_actions_callback,
                 name,
                 health=100,
                 interactable_tile_types=[],
                 interact_only_on_tile_below=True,
                 layout_callback_update_quad_tree = None):
        super().__init__(groups,
                         layout_callback_update_quad_tree = layout_callback_update_quad_tree )
        #print(f"name : {name}")
        self.hit_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        self.vulnerable = True
        self.sprite_type = "neutral"
        self.pos = pos
        self.obstacle_sprites = obstacle_sprites
        self.get_tile_valid_actions = get_tile_valid_actions_callback
        self.name = name
        self.health = health
        self.status = "idle"
        self.import_graphics()
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.interactable_tile_types = interactable_tile_types
        self.roam_direction_change_coef = 0.2
        self.direction_vector = ( random.choice([-1, 1]), random.choice([-1, 1]) )
        self.roam_walk_chance = 0.05
        self.interact_only_on_tile_below = interact_only_on_tile_below

    def import_graphics(self):
        self.animations = {"idle": [], "walking": []}
        main_path = f"../Graphics/Neutral/{self.name}/"
        for animation in self.animations.keys():
            full_path = main_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return(distance, direction)

    def roam(self,QuadTree,entity_quad_tree):

        #print("IM ROAMING BABY")
        interact = False
        if random.random() < self.roam_walk_chance:
            #print("RANDOM HIT !!")
            #print(f"status {self.status}")
            #print(f"self.direction {self.direction}")
            if self.status in ['walking','idle']:
                self.status = "walking" if self.status == "idle" else "idle"
            if random.random() < self.roam_direction_change_coef :
                self.direction_vector = ( random.choice([-1, 1]), random.choice([-1, 1]) )
            self.direction = pygame.math.Vector2( self.direction_vector ).normalize()

        if self.status == "walking":
            #print(f" self pos pre move {self.pos}")
            #print(f"PRE speed {self.speed}, direction {self.direction}, rect {self.rect}, hitbox {self.hitbox}")
            self.move(self.speed,
                      QuadTree=QuadTree,
                      entity_quad_tree=entity_quad_tree)
            #print(f" self pos post move {self.pos}")
            #print(f"POST speed {self.speed}, direction {self.direction}, rect {self.rect}, hitbox {self.hitbox}")
            
            interact, possible_interactions, position = self.check_interactable_tile()
            if interact:
                self.status = 'idle'
                self.direction = pygame.math.Vector2(0, 0)
                self.move(0, QuadTree=QuadTree, entity_quad_tree=entity_quad_tree)
                #print(possible_interactions)
                chosen_action = self.choose_action(possible_interactions)
                self.perform_action(chosen_action, position)



    def check_interactable_tile(self):
        """
        
        this function still lacks logic to randomly choose between various possible interaction types
        Eskimo only acts on tile below,
        Polarbear acts on any ()
        
        """
        
        
        position = self.rect.center
        position = ((position[0] // TILESIZE) * TILESIZE, (position[1] // TILESIZE) * TILESIZE)

        #print(self.sprite_type)
        
        tile_valid_actions = self.get_tile_valid_actions(position, self.interact_only_on_tile_below)
        #print(tile_valid_actions)
        if tile_valid_actions:
            
            #print(f"tile_valid_actions:{tile_valid_actions}")
            set_of_valid_actions = tile_valid_actions[1]
            tile_valid_actions = tile_valid_actions[0]
            
            #print(f"set of valid actions : {set_of_valid_actions}")
            #print(f"tile_valid_actions : {tile_valid_actions}")
            
            #print(self.interact_only_on_tile_below)
            if self.interact_only_on_tile_below:   ## Always true at the moment, 
                tile_valid_actions = tile_valid_actions.get('on')
                
                possible_interactions = set(tile_valid_actions).intersection(self.interactable_tile_types) # set conversion here is just a quick fix, i think i should output this as set but i see wierd complexity where i output set and list in some cases so i assume maybe elsewhere list is necessary  ?
                #print(possible_interactions)
                return True, possible_interactions, position
            else:
                
                
                possible_interactions = set_of_valid_actions.intersection(self.interactable_tile_types)
                #print("possible interactions")
                
                
                
                # I need to iterate over possible interactions and randomly choose one, lets see what the obj lookslike
                # I need to understand why i am getting the first index of the possible interactions
                # this is because it seems arbitrary
                
                if len(possible_interactions) > 0:
             
                    
                    return True, possible_interactions,position
        return False, set(),(0,0)

    
    def choose_action(self,possible_interactions, probabilities = None):
        
        if probabilities:
            chosen_key = random.choices(list(possible_interactions), weights=probabilities, k=1)[0]
            return chosen_key
        chosen_key = random.choice(list(possible_interactions))
        return chosen_key

    def perform_action(self, action,tile_pos):
        pass

    def check_interactable_tile_old(self):
        #print(f"rect center : {self.rect.center}")
        position = self.rect.center
        position = ( (position[0] // TILESIZE) * TILESIZE, (position[1] // TILESIZE) * TILESIZE )

                
    
        tile_valid_actions = self.get_tile_valid_actions(position,self.interact_only_on_tile_below)
        #print(tile_valid_actions)
        if tile_valid_actions:
            set_of_valid_actions = tile_valid_actions[1]# just splitting info from returned values , gives a dict and a set 
            tile_valid_actions  = tile_valid_actions[0]
            
            #print(f"tile valid actions : {}")
            
            ### Change from taking a single set of valid actions and applying them to the tile below to
            ##  figure out possible tiles to interact with
            ##  choose which tile (one your facing first)
            ##  rotate sprite to face that tile.
                
            if self.interact_only_on_tile_below:
                
                tile_valid_actions = tile_valid_actions.get('on')
                possible_interactions = set_of_valid_actions.intersection(self.interactable_tile_types)
                if len(possible_interactions) > 0:        
                    for possible_interaction in possible_interactions:
                        if random.random() < 0.1:  
                            #print(f"ATTEMPTING TO PERFORM ACTION: {possible_interaction}")
                            self.perform_action(possible_interaction,position)
            else:
                        # if multiple type of interaction to do choose here
                #print(possible_interactions)
                possible_interactions = set_of_valid_actions.intersection(self.interactable_tile_types)
                if len(possible_interactions) > 0:
                    possible_interaction = list(possible_interactions)[0]
                    # get all touching tiles you could do it on
                    possible_interaction_tiles = []
                    for tile_pos in tile_valid_actions.keys():
                        if possible_interaction in tile_valid_actions[tile_pos]:
                            possible_interaction_tiles.append(tile_pos)
                    
                    if random.random() > 0.9:
                        choice = random.choice(possible_interaction_tiles)
                        if choice =='right':    
                            position = (position[0] + TILESIZE, position[1])
                        if choice =='left':    
                            position = (position[0] - TILESIZE, position[1])
                        if choice =='above':    
                            position = (position[0] , position[1] - TILESIZE)
                        if choice =='below':    
                            position = (position[0] , position[1] + TILESIZE)
                        #print("performing action ")
                        self.perform_action( possible_interaction) 
                        


    def update(self,dt,QuadTree,entity_quad_tree):
        self.roam(QuadTree=QuadTree,entity_quad_tree=entity_quad_tree)
        self.animate()

    def animate(self):
        
        animation = self.animations[self.status]
        #print(f"animation: {animation}")
        self.frame_index += self.animation_speed
        #print(f"frame index: {self.frame_index}")
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
