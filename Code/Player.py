import pygame
from Support import import_folder
from Settings import *
from Entity import Entity
import os
from Inventory import Inventory
from PlayerConfiguration import PlayerConfiguration
from inputManager import InputManager
from AttackSelection import AttackSelection
from Settings import *
from Support import frames_to_masks

class BasePlayer(Entity):
    def __init__(self,
                 pos,
                 groups,
                 obstacle_sprites,
                 create_attack,
                 destroy_attack,
                 create_magic,
                 create_evasion,
                 initial_stats,
                 level,
                 input_manager,
                 character_assets,
                 QuadTree,
                 entity_quad_tree,
                 layout_callback_update_quad_tree = None):
        
        super().__init__(groups,layout_callback_update_quad_tree)
        
        #self.TILESIZE = TILESIZE * 0.4# hardcoded bs fix it.
        self.type = 'player'
        self.previous_tile = None
        self.power_level = 1
        self.inventory = Inventory(self, input_manager)
        
        self.level = level
        self.input_manager = input_manager
        self.last_p_press_time = 0
        self.last_i_press_time = 0
        self.last_q_press_time = 0
        # Graphics Setup
        self.import_player_assets(character_assets)
        self.status = "down"
        self.masks = self.convert_animations_to_masks(self.animations)
        # Movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites
        self.QuadTree = QuadTree
        # Weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # Magic
        self.magic_available = magic_data
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        self.attack_selection = AttackSelection(self, input_manager)


        # Evasions
        self.evasion_types = ['slide', 'create_ice_clone']  # SHOULD GO IN Setting.py like magic etc.
        self.create_evasion = create_evasion
        self.slide_end_time = None
        self.slide_duration = 300
        self.current_evasion_index = 0  # Start with the first evasion type
        self.can_switch_evasion = True
        self.evasion_switch_time = None
        self.switch_evasion_cooldown = 200
        
        
        # Stats    BAS ARE IN /Graphics/PlayerSelectionDict.json
        # self.base_stats = {"health": 1000,
        #                     "energy": 60,
        #                     "attack": 10,
        #                     "magic": 4,
        #                     "speed": 10, 
        #                     "strength": 5,
        #                     "intelligence":7,
        #                     "agility":6,
        #                     "charisma":3}
        
        
        
        self.stats  = initial_stats 
        self.player_config = PlayerConfiguration( input_manager = input_manager,
                                                  base_stats = self.stats,
                                                  remaining_points=2)   
        
        
        ## WL 
        # I need to set new magic , new energy, new health, there should be health recovery too.
        
        ### New neregy value, but magic need to be accounted for too, magic is jsut mana regen , right ? 
        
        #   I should add health regen here, add vitality.
        
        # 
        
        
        
        
        self.max_stats = {"health": 300, "energy": 140, "attack": 20, "magic": 10, "speed": 10}
        self.upgrade_cost = {"health": 100, "energy": 100, "attack": 100, "magic": 100, "speed": 100}
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.exp = 0
        self.speed = self.stats["speed"]
        self.speed_multiplier = 1 
        
        # Damage Timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 0

        # Import Sound
        self.weapon_attack_sound = pygame.mixer.Sound("../Audio/Sword.wav")
        self.weapon_attack_sound.set_volume(0.2)

        self.scale_animation()
        
         
    def scale_animation(self):
        if hasattr(self, "TILESIZE"):
            for state, frames in self.animations.items():
                for i, frame in enumerate(frames):
                    self.animations[state][i] = pygame.transform.scale(frame, (self.TILESIZE, self.TILESIZE))


    def import_player_assets(self, character_path):
        #print("\n\n attempt at import \n\n")
        #print(character_path)
        self.animations = {
            "up": [], "down": [], "left": [], "right": [],
            "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
            "right_attack": [], "left_attack": [], "up_attack": [], "down_attack": [],
            "slide_right":[],"slide_left":[]
        }

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
            
    def convert_animations_to_masks(self, animations_dict):
        masks = {}
        for key in animations_dict.keys():
            animation_set = animations_dict[key]
            mask_set = frames_to_masks(animation_set)
            masks.update( {key:mask_set} )
        return masks


    def update_derived_attributes(self):
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.speed = self.stats["speed"]
        self.magic_power = self.stats["magic"]

    def set_speed_multiplier(self, multiplier):
        """Set the speed multiplier to temporarily adjust the player's speed."""
        self.speed_multiplier = multiplier
        
        
        
    def pickup_item(self, item):
        print(f"item.effect_type:{item.effect_type}")
        print(dir(item))
        if hasattr(self,"TILESIZE"):
            print(self.TILESIZE)
        if item.effect_type == 'consumable':
            self.apply_item_effect(item.effect)  # A method to apply the item's effect (e.g., heal the player)
        else:
            self.inventory.add_item(item)  # Add non-consumable items to the inventory
        
    def input(self):
        current_time = pygame.time.get_ticks()
        
        if 'slide' in self.status:  # Input blocking for both evasions and attacks should be unified
            return 
        
        # Handle key releases
        released_keys = [key for key in self.input_manager.previous_key_states if self.input_manager.previous_key_states[key] and not self.input_manager.current_key_states[key]]
        for key in released_keys:
            if key == pygame.K_UP:
                self.direction.y = 0
            elif key == pygame.K_DOWN:
                self.direction.y = 0
            elif key == pygame.K_LEFT:
                self.direction.x = 0
            elif key == pygame.K_RIGHT:
                self.direction.x = 0
    
        # Handle key presses
        if not self.attacking:
            if self.input_manager.is_key_just_pressed(pygame.K_i):
                if current_time - self.last_i_press_time > 500:
                    self.level.toggle_inventory()
                    self.last_i_press_time = current_time
    
            if self.input_manager.is_key_pressed(pygame.K_LALT) or self.input_manager.is_key_pressed(pygame.K_RALT):
                if self.input_manager.is_key_just_pressed(pygame.K_q):
                    if current_time - self.last_q_press_time > 500:
                        self.level.toggle_attack_selection()
                        self.last_q_press_time = current_time        
    
            if self.input_manager.is_key_pressed(pygame.K_UP):
                self.direction.y = -1
                self.status = "up"
            elif self.input_manager.is_key_pressed(pygame.K_DOWN):
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0
    
            if self.input_manager.is_key_pressed(pygame.K_RIGHT):
                self.direction.x = 1
                self.status = "right"
            elif self.input_manager.is_key_pressed(pygame.K_LEFT):
                self.direction.x = -1
                self.status = "left"
            else:
                self.direction.x = 0
    
            if self.input_manager.is_key_pressed(pygame.K_SPACE):
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()
    
            if self.input_manager.is_key_pressed(pygame.K_LCTRL):
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]["strength"] + self.stats["magic"]
                cost = list(magic_data.values())[self.magic_index]["cost"]
                self.create_magic(style, strength, cost)
    
            if self.input_manager.is_key_pressed(pygame.K_q) and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                self.weapon = list(weapon_data.keys())[self.weapon_index]
    
            if self.input_manager.is_key_pressed(pygame.K_e) and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                if self.magic_index < len(list(magic_data.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0
                self.magic = list(magic_data.keys())[self.magic_index]
                
            if self.input_manager.is_key_just_pressed(pygame.K_r) and self.can_switch_evasion:
                self.can_switch_evasion = False
                self.evasion_switch_time = current_time
                self.current_evasion_index = (self.current_evasion_index + 1) % len(self.evasion_types)
    
            if self.input_manager.is_key_just_pressed(pygame.K_c):
                direction = self.get_direction_as_string()
                evasion_type = self.evasion_types[self.current_evasion_index]
                self.create_evasion(evasion_type, direction)
                
            if self.input_manager.is_key_just_pressed(pygame.K_p):
                if current_time - self.last_p_press_time > 500:
                    self.level.toggle_menu()
                    self.last_p_press_time = current_time

    def get_direction_as_string(self):
        return "right" if self.direction.x >= 0 else "left"


    def get_status(self):
        #print(f"in get_status first status : {self.status}")
        #print(f"IS SLIDE IN self.status :{'slide' in self.status}")
        if 'slide' in self.status:
            self.maintain_slide_status()
        else:
            if self.direction.x == 0 and self.direction.y == 0:
                if not "idle" in self.status and not "attack" in self.status:
                    self.status += "_idle"
            else:
                if self.attacking:
                    self.direction.x = 0
                    self.direction.y = 0
                    if not "attack" in self.status:
                        if "idle" in self.status:
                            self.status = self.status.replace("_idle", "_attack")
                        else:
                            self.status = self.status + "_attack"
                else:
                    if "attack" in self.status:
                        self.status = self.status.replace("_attack", "")

    def maintain_slide_status(self):
       #print(f"first in maintain_slide_status : {self.status}")
       #print( hasattr(self, 'pending_status_reset') )
        # Continue sliding motion, and block other interactions
        if hasattr(self, 'pending_status_reset') and self.pending_status_reset:
            # The slide is about to end; prepare to reset status
           #print(f"has attribute : {self.status} attribute:{self.pending_status_reset}")
            self.status = self.pending_status_reset
           #print(f"status after being reset : {self.status}")
            delattr(self, 'pending_status_reset')
        else:
           #print(f"attribute to reset does not exist and now we in here , first status : {self.status}")
            # Block inputs that could change status
            self.attacking = False
            self.direction.x = 0
            self.direction.y = 0
           #print(f"attribute to reset does not exist and now we in here , last status : {self.status}")

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]["cooldown"]:
                self.attacking = False
                self.destroy_attack()
        if not self.can_switch_evasion:
            if current_time - self.evasion_switch_time >= self.switch_evasion_cooldown:
                self.can_switch_evasion = True
                
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
       #print("\n\nANIMATIONS#print \n\n")
       #print(self.frame_index)
       #print(self.status)
        #print(self.animations)
        animation = self.animations[self.status]
        masks = self.masks[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.mask = masks[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats["attack"]
        weapon_damage = weapon_data[self.weapon]["damage"]
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats["magic"]
        spell_damage = magic_data[self.magic]["strength"]
        return base_damage + spell_damage

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def player_death(self):
        if self.health <= 0:
            sys.exit()

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def energy_recovery(self):
        if self.energy < self.stats["energy"]:
            self.energy += 0.05 * self.stats["magic"]
        else:
            self.energy = self.stats["energy"]


    def health_recovery(self):
        if self.health < self.stats["health"]:
            self.health += 0.05 * self.stats["vitality"]
        else:
            self.health = self.stats["health"]


    def update(self, QuadTree,entity_quad_tree, dt=None,layout_switch= False):#
        
    
        #print(f"player attributes:{self.stats}")
    
        #print(self.rect.center[0]/TILESIZE)
        #print(self.rect.center[1]/TILESIZE)
        current_time = pygame.time.get_ticks()
        if self.slide_end_time and current_time >= self.slide_end_time:
            ### THIS SHOULD BE A SLIDE END METHOD, CLEARLY
            self.status = self.status.replace("slide_", "") + "_idle"
            self.set_speed_multiplier(1)
            self.rect.y -= 20
            self.hitbox.center = self.rect.center
            self.slide_end_time = None  # Reset the timer
            
       #print(f"status pre input{self.status} {self.rect.x}")
       
        #if not layout_switch:
             
        self.input()
       #print(f"status pre cooldowns{self.status} {self.rect.x}")
        self.cooldowns()
       #print(f"status pre getstatus{self.status}  {self.rect.x}")
        self.get_status()
       #print(f"status pre animate{self.status}  {self.rect.x}")
        self.animate()
       #print(f"status pre move{self.status}  {self.rect.x}")
        
        if'slide' in self.status:
            self.move_slide()   
            
        else:
            #print("SPEEDS")
            #print(self.stats['speed'])
            #print(self.speed_multiplier)
            #print()
            
            self.move(self.stats["speed"],QuadTree,entity_quad_tree)  # Regular movement
            self.collision(QuadTree, entity_quad_tree)
        #print(self.stats["speed"])
       #print(f"status pre erecov{self.status} {self.rect.x}")
        self.energy_recovery()
        self.health_recovery()
       #print(f"status pre Player death{self.status} {self.rect.x}")
        self.player_death()
        # Check if there's a pending status reset after an evasion and reset status
       #print(f"pending_status condition _{hasattr(self, 'pending_status_reset') } ")
        if hasattr(self, 'pending_status_reset') and self.pending_status_reset:
           #print(f"status pre inside resetting loop {self.status} {self.rect.x}")
            self.status = self.pending_status_reset  # Reset status to idle or other appropriate status
           #print(f"status pre inside resetting loop POST{self.status} {self.rect.x}")
            self.set_speed_multiplier(1)  # Reset speed to normal
            delattr(self, 'pending_status_reset')  # Remove the attribute to prevent repeated resets

    def move_slide(self):
        # Move the player in the slide direction with increased speed
        
        slide_direction = self.status.split('_')[1]
        self.create_evasion( "slide", slide_direction )
       #print(f"IN MOVE SLIDE - {slide_direction} ")
       #print(f"self.rect pre {self.rect.x}")
        if slide_direction == "right":
            self.rect.x += self.stats["speed"] * self.speed_multiplier
        elif slide_direction == "left":
            self.rect.x -= self.stats["speed"] * self.speed_multiplier
       #print(f"self.rect post {self.rect.x}")
        # Update hitbox to match the new rect
        self.hitbox.center = self.rect.center
        

class SpecificPlayer(BasePlayer):
    def __init__(self,
                 selected_player_info_dir,
                 pos,
                 groups,
                 obstacle_sprites, 
                 create_attack,
                 destroy_attack,
                 create_magic,
                 create_evasion,
                 initial_stats,
                 level,
                 input_manager,
                 QuadTree,
                 entity_quad_tree,
                 layout_callback_update_quad_tree = None):
        
        character_assets = selected_player_info_dir
        super().__init__(pos,
                         groups,
                         obstacle_sprites,
                         create_attack,
                         destroy_attack,
                         create_magic,
                         create_evasion,
                         initial_stats,
                         level,
                         input_manager,
                         character_assets,
                         QuadTree,
                         entity_quad_tree,
                         layout_callback_update_quad_tree )
        

        # Set the initial image for the specific player
        self.image = pygame.image.load(character_assets + "down_idle/0.png").convert_alpha()
#        print(character_assets + "/down_idle/0.png")
        self.rect = self.image.get_rect(topleft=pos)
         # Initialize hitbox for SpecificPlayer
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET["player"])
# You can add more specific player classes here in a similar fashion.
