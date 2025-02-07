import pygame
from Settings import *
from Entity import Entity
from Support import *
import os
from hashRect import HashableRect
from CombatStrategy import MeleeCombatStrategy,RangedCombatStrategy,MixedCombatStrategy
import random
import os
import cv2
    
# This is for file importing but is in Main.py anyways
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Friendly(Entity):
    def __init__(self,
                 monster_name,
                 pos,
                 groups,
                 obstacle_sprites,
                 combat_context,
                 persistent,
                 layout_callback_update_quad_tree = None,
                 animations_left_right_indicator=True,
                 special_attacks=None,
                 item_drop_info=None,
                 combat_config=None):

        if "update_quad_tree" in combat_context.keys():
            layout_callback_update_quad_tree = combat_context["update_quad_tree"]
        else:
            layout_callback_update_quad_tree = None
        
        # General Setup
        super().__init__(groups=groups,
                         layout_callback_update_quad_tree = layout_callback_update_quad_tree)
        self.groups = groups
        self.sprite_type = "friendly"
        
        
        
        self.special_attacks = special_attacks or {} # NOT USED RIGHT NOW
        self.combat_config = combat_config or {}    # ALSO NEVER PASSED, IS FROM MONSTER INFO NOT USED RIGHT NOW
        self.combat_context = combat_context or {}
        
        
        if item_drop_info:
            self.item_drop_info = item_drop_info
        self.animations_left_right_indicator = animations_left_right_indicator
        
        # Graphics Setup
        if animations_left_right_indicator:
            self.import_graphics_left_right(monster_name)
        else:
            self.import_graphics(monster_name)
        
        self.status = "idle"
        self.direction_string = 'right'
        if self.animations_left_right_indicator:
            self.image = self.animations[self.status][self.direction_string][self.frame_index]
        else:
            self.image = self.animations[self.status][self.frame_index]

        # Movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites
        self.direction_update_time = 500
        self.last_direction_update_time = pygame.time.get_ticks()

        # Stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info["health"]
        self.exp = monster_info["exp"]
        self.speed = monster_info["speed"]
        self.resistance = monster_info["resistance"]
        
        #### All in combat config now
        self.combat_config = monster_info["combat_config"]
        self.attack_type = monster_info["attack_type"]
        

        # TODO: still a bunch of stuff not in the combat config...look at these variables below.
        #         just used for cooldowns which is done badly anyway should have each attack on cooldown
        #         must define classes for attacks i think
        
        #         parrys are also passed separately to the combat strategy for some reason 
        
                # attack type used to define combat strategy sub class.
        
        # END TODO
        
        self.melee_attacks = self.combat_config.get("melee_attacks", [])
        self.ranged_attacks = self.combat_config.get("ranged_attacks", [])
        self.melee_parry_chance = self.combat_config.get("melee_parry_chance", 0)
        self.projectile_parry_chance = self.combat_config.get("projectile_parry_chance", 0)
        self.parry_cooldown = self.combat_config.get("parry_cooldown", 1000)


        #### 

        self.masks = self.convert_animations_to_masks(self.animations)
        self.mask = None

        # Player Interaction
        self.can_attack = True
        self.attack_time = pygame.time.get_ticks()
        
        
        ### Is this series of cooldowns used ? urg cool down done super wierd
        
        # TODO: cooldowns just takes the max cooldown from all attacks, i can do better than this
        
        self.attack_cooldown = max([attack["cooldown"] for attack in self.melee_attacks + self.ranged_attacks], default=400)
        self.persistent = persistent

        # Attacks
        self.last_attack_action_time = 0
        self.attack_action_cooldown = self.attack_cooldown
        self.last_parry_time = 0

        # Freeze logic 
        self.frozen = False  
        self.freeze_time = 0

        # Invincibility Timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # Sounds
        self.death_sound = pygame.mixer.Sound("../Audio/Death.wav")
        self.hit_sound = pygame.mixer.Sound("../Audio/Hit.wav")
        self.attack_sound = pygame.mixer.Sound(monster_info["attack_sound"])
        self.death_sound.set_volume(0.6)
        self.hit_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.3)
        
        # Combat Strategy Setup
        parry_effects = {
            "melee_parry_chance": self.melee_parry_chance,
            "projectile_parry_chance": self.projectile_parry_chance,
            "parry_cooldown": self.parry_cooldown
        }
        #self.redirect_projectile_callback = redirect_projectile_callback

        if self.attack_type == "melee":
            self.combat_strategy = MeleeCombatStrategy(self.melee_attacks,
                                                       parry_effects,
                                                       movement_behavior=None,
                                                       combat_context=self.combat_context,
                                                       special_attacks=self.special_attacks
                                                       #redirect_projectile_callback = redirect_projectile_callback,
                                                       #fire_projectile = self.fire_projectile
                                                       )
        elif self.attack_type == "ranged":
            self.combat_strategy = RangedCombatStrategy(self.ranged_attacks,
                                                        parry_effects,
                                                        movement_behavior=None,
                                                        #redirect_projectile_callback = redirect_projectile_callback,
                                                        #fire_projectile = self.fire_projectile
                                                        combat_context=self.combat_context,
                                                       special_attacks=self.special_attacks
                                                        )
        elif self.attack_type == "mixed":
            self.combat_strategy = MixedCombatStrategy(self.melee_attacks,
                                                       self.ranged_attacks,
                                                       parry_effects,
                                                       movement_behavior=None,
                                                       combat_context=self.combat_context,
                                                       special_attacks=self.special_attacks
                                                       #redirect_projectile_callback = redirect_projectile_callback,
                                                       #fire_projectile = self.fire_projectile,
                                                       
                                                       )
 
        else:
            # just coz i dont have settings correctly made for al lmonsters atm.
            self.combat_strategy = MeleeCombatStrategy(self.melee_attacks,
                                                       parry_effects,
                                                       movement_behavior=None,
                                                       combat_context=self.combat_context,
                                                       special_attacks=self.special_attacks
                                                       #redirect_projectile_callback = redirect_projectile_callback,
                                                       #fire_projectile = self.fire_projectile
                                                       )
        

    
    
    def scale_animations(self, scale_factor):
        for status, animations in self.animations.items():
            if isinstance(animations, dict):
                for direction, frames in animations.items():
                    self.animations[status][direction] = [pygame.transform.scale(frame, (int(frame.get_width() * scale_factor), int(frame.get_height() * scale_factor))) for frame in frames]
            else:
                self.animations[status] = [pygame.transform.scale(frame, (int(frame.get_width() * scale_factor), int(frame.get_height() * scale_factor))) for frame in animations]

    
    ## TODO: place this in support
    def convert_animations_to_masks(self, animations_dict):
        masks = {}
        main_folder = "../Graphics/Masks"
        os.makedirs(main_folder, exist_ok=True)
    
        if self.animations_left_right_indicator:
            for key, animation_set_left_right in animations_dict.items():
                monster_folder = os.path.join(main_folder, self.monster_name)
                os.makedirs(monster_folder, exist_ok=True)
                
                masks_temp = {}
                for left_right_key, animation_set in animation_set_left_right.items():
                    direction_folder = os.path.join(monster_folder, left_right_key)
                    os.makedirs(direction_folder, exist_ok=True)
    
                    mask_frames = frames_to_masks(animation_set)
                    masks_temp[left_right_key] = mask_frames
                    
                    # Save each mask frame as an image
                    for i, mask in enumerate(mask_frames):
                        if mask is not None:  # Check if mask exists
                            # Save the mask as an image
                            image_path = os.path.join(direction_folder, f"{key}_{left_right_key}_mask_{i}.png")
                            pygame.image.save(mask.to_surface(), image_path)
                        
                masks[key] = masks_temp
        else:
            for key, animation_set in animations_dict.items():
                monster_folder = os.path.join(main_folder, self.monster_name)
                os.makedirs(monster_folder, exist_ok=True)
                
                direction_folder = monster_folder
    
                mask_frames = frames_to_masks(animation_set)
                masks[key] = {"default": mask_frames}
                
                # Save each mask frame as an image
                for i, mask in enumerate(mask_frames):
                    if mask is not None:  # Check if mask exists
                        # Save the mask as an image
                        image_path = os.path.join(direction_folder, f"{key}_mask_{i}.png")
                        pygame.image.save(mask.to_surface(), image_path)
        
        return masks



        
    def freeze(self, duration=3000):
        """Freeze the unit, stopping all movement and actions."""
        self.frozen = True
        self.freeze_time = pygame.time.get_ticks()
        self.freeze_duration = duration
        self.frozen_image = self.apply_frozen_effect(self.image)  # Apply effect and save
        
    def apply_frozen_effect(self, image):
        """Applies a turquoise color overlay only to the non-transparent parts of an image."""
        frozen_image = image.copy()  # Make a copy to not alter the original
        turquoise_overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        
        # Fill the overlay with turquoise color
        turquoise_overlay.fill((64, 224, 208, 128))  # Semi-transparent turquoise
        
        # Create a mask using the alpha value of the original image
        alpha_mask = pygame.surfarray.pixels_alpha(image).copy()
        
        # Set this alpha mask to the turquoise overlay
        pygame.surfarray.pixels_alpha(turquoise_overlay)[:] = alpha_mask
        
        # Blit the turquoise overlay onto the frozen image using BLEND_RGBA_MULT for color multiply
        frozen_image.blit(turquoise_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return frozen_image


    def get_direction_as_string(self):
        return "right" if self.direction.x >= 0 else "left"

    
     
    
    def thaw(self):
        """Thaw the enemy, resuming normal behavior."""
        #print('THAWED')
        self.frozen = False
        #print(self.status)
        #print(self.animations[self.status])
        #print(self.direction_string  )
        #print(self.animations_left_right_indicator)
        if self.animations_left_right_indicator:            
            self.image = self.animations[self.status][self.direction_string][int(self.frame_index)]
        else:
            self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        


    def is_dead(self):
        """Check if the unit is dead."""
        return self.health <= 0

    
    
    def import_graphics_left_right(self, name):
        self.animations = {
            "idle": {"right": [], "left": []}, 
            "move": {"right": [], "left": []}, 
            "attack": {"right": [], "left": []}
        }
        main_path = f"../Graphics/Monsters/{name}/"
    
        # Standard animations
        for animation in self.animations.keys():
            self.animations[animation]["right"] = import_folder(main_path + animation)
            self.animations[animation]["left"] = [pygame.transform.flip(img, True, False) for img in self.animations[animation]["right"]]
    
        # Check for SpecialAttacks folder
        special_attacks_path = os.path.join(main_path, "SpecialAttacks")
        if os.path.exists(special_attacks_path) and os.path.isdir(special_attacks_path):
            for special_attack in os.listdir(special_attacks_path):
                special_attack_path = os.path.join(special_attacks_path, special_attack)
                if os.path.isdir(special_attack_path):
                    self.animations[special_attack] = {"right": [], "left": []}
                    self.animations[special_attack]["right"] = import_folder(special_attack_path)
                    self.animations[special_attack]["left"] = [pygame.transform.flip(img, True, False) for img in self.animations[special_attack]["right"]]


    def import_graphics(self, name):
        self.animations = {"idle": [], "move": [], "attack": []}
        main_path = f"../Graphics/Monsters/{name}/"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)
        # print(f"name : {name}")
        # print(f"path : {main_path + animation}")
        # print(f"Loaded animations for {name}: {self.animations}")


### First change : i guess i need the distance of the enemy he is attacking


    def get_enemy_distance_direction(self, enemy):
        #print("getting player distance")
        friendly_vec = pygame.math.Vector2(self.rect.center)
        enemy_vec = pygame.math.Vector2(enemy.rect.center)
        #print(player_vec)
        distance = (enemy_vec - friendly_vec).magnitude()
        #print(f"player : {player_vec}")
        #print(f"enemy : {enemy_vec}")
        #print(distance)
        
        if distance > 0:
            direction = (enemy_vec - friendly_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return(distance, direction)

    # not used , just reference for writing above function
    def get_player_distance_direction(self, player):
        #print("getting player distance")
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        #print(player_vec)
        distance = (player_vec - enemy_vec).magnitude()
        #print(f"player : {player_vec}")
        #print(f"enemy : {enemy_vec}")
        #print(distance)
        
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return(distance, direction)


    # second change. 
    # Player distance will be relevant, if he is too far from the player, and he has some attribute (Summoned)
    # Then he will teleport near player ? or just start running back ? 
    
    # Status's will be different too, he should have follow if he is summmoned, move will move towards enemy
    
    
    def get_status(self, enemies, player):
        enemy = get_closest_enemy(enemies)
        distance = self.get_enemy_distance_direction(enemy)[0]

        # will not have this here actually
        if distance >= self.teleport_distance:
            self.teleport_back(player)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != "attack":
                self.frame_index = 0
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "move"
    #@profile
    
    
    
    def actions(self, player, quadtree=None):
        if self.status != "Summoning":  # TODO: Only perform actions if not summoning - should be if casting, need logic here 
            self.combat_strategy.decide_action(self, player)
            self.combat_strategy.move(self, player)
            if self.status == "attack":
                self.combat_strategy.execute_attack(self, player)
            self.combat_strategy.parry(self, player, quadtree)
        else:
            self.combat_strategy.execute_attack(self, player)
        
    
    


    #@profile
    def animate(self):
        
       # print(self.status)
       # print(self.frame_index)
       # print(self.can_attack)
        
        
        
        
        if self.frozen:
            #print("FROZEN")
            self.image = self.frozen_image
            new_rect = self.image.get_rect(center=self.hitbox.center)
            #if new_rect.size != self.rect.size:
                
                #print(f"Rect size mismatch: original {self.rect.size}, new {new_rect.size}")
            self.rect = new_rect
        else:
        
            if self.animations_left_right_indicator:
                direction_string = self.get_direction_as_string()
                animation = self.animations[self.status][direction_string]  
                #print(self.sprite_type)
                #print(self.monster_name)
                #print(self.masks)
                masks = self.masks[self.status][direction_string]
            else:
                animation = self.animations[self.status]
                masks = self.masks[self.status]
            
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                if self.status == "attack":
                    self.can_attack = False
                    self.status = "idle"
                    ## TODO: THIS BEING HERE AGAIN IS A MESS ITS TO FORCE CHANGE IN ANIMATION RIGHT NOW, NOT EVEN SURE IT HELPS ( WAS STUK IN ATTACK ANIMATION TOO LONG )
                    if self.animations_left_right_indicator:
                        direction_string = self.get_direction_as_string()
                        animation = self.animations[self.status][direction_string]   
                        masks = self.masks[self.status][direction_string]
                    else:
                        animation = self.animations[self.status]
                        masks = self.masks[self.status]
                    
                self.frame_index = 0
    
            self.image = animation[int(self.frame_index)]
            self.mask = masks[int(self.frame_index)]
            self.rect = self.image.get_rect(center = self.hitbox.center)
    
            if not self.vulnerable:
                alpha = self.wave_value()
                self.image.set_alpha(alpha)
            else:
                self.image.set_alpha(255)
                
                
    #@profile
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True
    #@profile
    
    # TODO: intervention 3
    # Need to get damage from enemies like player
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
    #@profile
    def check_death(self):
        if self.health <= 0:
            self.layout_callback_update_quad_tree( obstacle_sprite = HashableRect( self.rect, self.id ),
                                                   remove_existing= True,
                                                   alive = False )# confusing its a callback passed to all entities, this is child , it can use it right ? 
            self.kill()
            #### TODO , add frozen or not end to monster name for frozen death particles.
            self.combat_context["trigger_death_particles"](self.rect.center, self.monster_name)
            #self.combat_context["add_exp"](self.exp)
            self.death_sound.play()
            
    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance
    #@profile
    
    
    ### Why is there update and enemy update, i think update is not being used , right ? 
    #  all the freeze and move etc logic is in actions, no ? no... its in "animate".
    
    def update(self, QuadTree , entity_quad_tree, dt = None):   
        current_time = pygame.time.get_ticks()
        if self.frozen and current_time - self.freeze_time > self.freeze_duration:
            self.thaw()
        if not self.frozen and self.status == 'move':
            self.move(speed = self.speed,
                      QuadTree = QuadTree ,
                      entity_quad_tree = entity_quad_tree)
            self.hit_reaction()
        self.animate()
        self.cooldowns()
        self.check_death()


    #@profile
    def enemy_update(self, player, quadtree=None):
        if not self.frozen:
            #self.get_status(player)
            self.actions(player,quadtree)
