import random
import pygame
from pygame.math import Vector2
from  hashRect import HashableRect



class CombatStrategy:
    def __init__(self,
                 parry_effects,
                 movement_behavior,
                 #redirect_projectile_callback,
                 #fire_projectile,
                 combat_context = [],
                 special_attacks = None
                 ):
        
        self.parry_effects = parry_effects
        self.movement_behavior = movement_behavior
        self.combat_context = combat_context
        
        #self.redirect_projectile_callback = redirect_projectile_callback
        #self.fire_projectile = fire_projectile # TODO : probably not necessary in basic combat strategy should be in ranged.
        self.special_attacks = special_attacks or []
        
    def decide_action(self, enemy, player):
        raise NotImplementedError

    def execute_attack(self, enemy, player):
        raise NotImplementedError

    def move(self, enemy, player):
        raise NotImplementedError

    def parry(self, enemy, player, quadtree):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_parry_time < self.parry_effects['parry_cooldown']:
            return

        if self.parry_effects['melee_parry_chance'] > 0:
            # Handle melee parry logic elsewhere
            pass  

        nearby_projectiles = quadtree.hit(HashableRect(enemy.rect, enemy.id, None, 'magic'))
        for projectile_rect in nearby_projectiles:
            
            
            ## This is the first issue, attack_radius is not uniquely defined, its melee attack radius
            #  really, im just changing config name
            
            
            if Vector2(projectile_rect.rect.center).distance_to(enemy.rect.center) < enemy.combat_config["melee_attack_radius"]:
                if random.random() < self.parry_effects['projectile_parry_chance']:
                    
                    ## TODO: justs configure better because we are running random to check if its bigger than 0 here when we pass it
                    #        What happens when i just dont have it in config ? maybe its fine to just not
                    #        configure it, 
                    
                    direction_vector = Vector2(player.rect.center) - Vector2(projectile_rect.rect.center)
                    if direction_vector.length() > 0:
                        direction_vector.normalize_ip()
                        self.combat_context["redirect_projectile"](projectile_rect._id, direction_vector)
                        enemy.last_parry_time = current_time

    def handle_special_attacks(self, enemy, player):
        #print(f"Checking for special attacks {self.special_attacks}")
        random.shuffle(self.special_attacks)
        current_time = pygame.time.get_ticks()
        # Check for ongoing casting first
        for attack in self.special_attacks:
            #print(f"checking summoning :{attack}")
            if attack.name == "SummonIceGhosts" and attack.is_casting:
                #print("SUMMONNING AND READY TO UPDATE")
                attack.update(enemy, player, self.combat_context)
                #print(f"SUMMONNING AND READY TO UPDATE post status {enemy.status}")
                return True  # Skip other actions if SummonIceGhosts is casting

        # Execute special attacks if ready and conditions are met
        for attack in self.special_attacks:
            if attack.is_ready(current_time) and attack.can_trigger(enemy, player):
                #print(f"Executing special attack: {attack.name}")
                attack.execute(enemy, player, self.combat_context)
                if attack.name == "SummonIceGhosts":
                    attack.update(enemy, player, self.combat_context)
                    return True  # Skip other actions if SummonIceGhosts is casting
                return True  # Skip other actions if a special attack is used

        return False


class MeleeCombatStrategy(CombatStrategy):
    def __init__(self,
                 melee_attacks, 
                 parry_effects, 
                 movement_behavior,
                 combat_context,
                 special_attacks = None
                 #redirect_projectile_callback,
                 #fire_projectile
                 ):
        super().__init__(parry_effects,
                         movement_behavior,
                         combat_context,
                         special_attacks
                         #redirect_projectile_callback,
                         #fire_projectile
                         ) 
        self.melee_attacks = melee_attacks
        

    def decide_action(self, enemy, player):
        # assumes offensive stance initially
        # this guy has no other stance atm anyway
        if not hasattr(enemy,"movement_state") :
            enemy.movement_state = 'offensive'
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.combat_config['melee_attack_radius'] and enemy.can_attack:
            enemy.current_attack_type = "melee"
            enemy.movement_state = 'offensive'
            enemy.status = "attack"
        elif distance <= enemy.combat_config['notice_radius'] :
            enemy.current_attack_type = None
            enemy.movement_state = 'offensive'
            enemy.status = "move"
        else:
            enemy.current_attack_type = None
            enemy.status = "idle"
            

    def execute_attack(self, enemy, player):
        if self.handle_special_attacks(enemy, player):
            return 
        
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "melee":
                distance_to_player = Vector2(enemy.rect.center).distance_to(player.rect.center)
                if distance_to_player <= enemy.combat_config["melee_attack_radius"]:
                    attack = random.choice(self.melee_attacks)
                    self.combat_context["damage_player"](attack['damage'], "melee")
                    enemy.attack_sound.play()
                    enemy.attack_cooldown = attack['cooldown']
                    enemy.direction = Vector2(0, 0) 
    
    def move(self, enemy, player):
        if enemy.status != "attack":  # Only move if not attacking
            distance, direction = enemy.get_player_distance_direction(player)
            if enemy.movement_state == 'offensive':
                enemy.direction = direction
            elif enemy.movement_state == 'defensive':
                enemy.direction = -direction
            elif enemy.movement_state == 'evasive':
                enemy.direction = -direction + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            enemy.status = 'move'
        else:
            enemy.direction = Vector2(0, 0) 


class RangedCombatStrategy(CombatStrategy):
    def __init__(self,
                 ranged_attacks, 
                 parry_effects, 
                 movement_behavior,
                 combat_context,
                 special_attacks = None
                 #redirect_projectile_callback,
                 #fire_projectile
                 ):
        super().__init__(parry_effects,
                         movement_behavior,
                         combat_context,
                         special_attacks
                         #redirect_projectile_callback,
                         #fire_projectile
                         )
        self.ranged_attacks = ranged_attacks

    def decide_action(self, enemy, player):
        if not hasattr(enemy,"movement_state") :
            enemy.movement_state = 'defensive'
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.combat_config["ranged_attack_radius"] and enemy.can_attack:
            enemy.current_attack_type = "ranged"
            enemy.movement_state = 'defensive'
            enemy.status = "attack"
        else:
            enemy.current_attack_type = None
            enemy.movement_state = 'defensive'
            enemy.status = "move"

    def execute_attack(self, enemy, player):
        if self.handle_special_attacks(enemy, player):
            return 
        
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "ranged":
                attack = random.choice(self.ranged_attacks)
                self.combat_context["fire_projectile"](enemy_pos=enemy.rect.center,
                                                     target_pos=player.rect.center,
                                                     projectile_type=attack['type'],
                                                     groups=enemy.groups)
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
                enemy.direction = Vector2(0, 0) 
    
    def move(self, enemy, player):
        if enemy.status != "attack":  # Only move if not attacking
            distance, direction = enemy.get_player_distance_direction(player)
            if enemy.movement_state == 'defensive':
                enemy.direction = -direction
            elif enemy.movement_state == 'evasive':
                enemy.direction = -direction + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            enemy.status = 'move'
        else:
            enemy.direction = Vector2(0, 0)  


class MixedCombatStrategy(CombatStrategy):
    def __init__(self,
                 melee_attacks,
                 ranged_attacks,
                 parry_effects, 
                 movement_behavior,
                 combat_context,
                 special_attacks = None
                 #redirect_projectile_callback,
                 #fire_projectile
                 ):
        super().__init__(parry_effects,
                         movement_behavior,
                         combat_context,
                         special_attacks
                         #redirect_projectile_callback,
                         #fire_projectile
                         )
        self.melee_attacks = melee_attacks
        self.ranged_attacks = ranged_attacks
        self.last_evasive_change_time = pygame.time.get_ticks()
        self.evasive_direction  = Vector2(0,0)
        self.evasion_duration = None
        self.evasion_start_time = None

        
    def decide_action(self, enemy, player):
        if not hasattr(enemy,"movement_state") :
            enemy.movement_state = 'defensive'
        distance, _ = enemy.get_player_distance_direction(player)
        #print(f"decide action distance ; {distance}")
        #print(f" mele radiius: {enemy.combat_config['melee_notice_radius'] }")
        #print(f"ranged radiius: {enemy.combat_config['ranged_attack_radius'] }")

        if distance <= enemy.combat_config["melee_attack_radius"] and enemy.can_attack:
            enemy.current_attack_type = "melee"
            enemy.movement_state = 'offensive'
            enemy.status = "attack"
        elif distance <= enemy.combat_config["melee_notice_radius"] and enemy.can_attack:
            enemy.current_attack_type = "melee"
            enemy.movement_state = 'offensive'
            enemy.status = "move"
        elif distance <= enemy.combat_config["ranged_attack_radius"] and enemy.can_attack:
            enemy.current_attack_type = "ranged"
            enemy.movement_state = 'defensive'
            enemy.status = "attack"
        else:
            enemy.current_attack_type = None
            enemy.movement_state = 'evasive'
            enemy.status = "move"

        # print(f"in decide actions mixed strat")
        # print(f"movement state : {enemy.movement_state}")
        # print(f"attack type : {enemy.current_attack_type}")

    def execute_attack(self, enemy, player):
        
        
        # print(f"in execute attack")
        # print(f"melee attacks : {self.melee_attacks}")
        # print(f"range attacks : {enemy.ranged_attacks}")
        # if hasattr(enemy,"special_attacks" ):
            
        #     print(f"special attacks: {enemy.special_attacks}")

        #print(f"current attack type  : {enemy.current_attack_type}")

        if self.handle_special_attacks(enemy, player):
            
            return 
        
        current_time = pygame.time.get_ticks()
        attack = []
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "melee":
                distance_to_player = Vector2(enemy.rect.center).distance_to(player.rect.center)
                if distance_to_player <= enemy.combat_config["melee_attack_radius"]:
                    
                    attack = random.choice(self.melee_attacks)
                    self.combat_context["damage_player"](attack['damage'], "melee")
                    enemy.attack_sound.play()
                    enemy.attack_cooldown = attack['cooldown']

            elif enemy.current_attack_type == "ranged":
                attack = random.choice(self.ranged_attacks)
                self.combat_context["fire_projectile"](enemy_pos=enemy.rect.center,
                                     target_pos=player.rect.center,
                                     projectile_type=attack['type'],
                                     groups=enemy.groups)
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
            enemy.direction = Vector2(0, 0)  
                
        
        # print(f"in execute attack mixed strat")
        # print(f"attack : {attack}")
        # print(f"special attacks : {enemy.special_attacks}")
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        current_time = pygame.time.get_ticks()

        # Get the notice radius from the combat config
        notice_radius = enemy.combat_config['notice_radius']

        if distance > notice_radius:
            enemy.status = 'idle'
            enemy.direction = Vector2(0, 0)
            return

        if enemy.status != "attack":  # Only move if not attacking
            if enemy.movement_state == 'offensive':
                enemy.direction = direction
            elif enemy.movement_state == 'defensive':
                enemy.direction = -direction
            elif enemy.movement_state == 'evasive':
                # Get the shooting range from the combat config
                shooting_range = enemy.combat_config['ranged_attack_radius']

                if distance <= shooting_range:
                    # Move away from the player
                    if self.evasion_start_time is None or self.evasion_duration is None:
                        self.evasion_start_time = current_time
                        self.evasion_duration = random.gauss(enemy.combat_config['evasive_change_interval'], enemy.combat_config['evasive_change_interval'] * 0.2)

                    elapsed_time = current_time - self.evasion_start_time

                    if elapsed_time < self.evasion_duration:
                        if self.evasive_direction is None:
                            evasive_base_direction = -direction
                            random_variation = Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                            combined_direction = (evasive_base_direction + random_variation).normalize()
                            self.evasive_direction = combined_direction

                        enemy.direction = self.evasive_direction
                    else:
                        if current_time - self.evasion_start_time < enemy.combat_config['evasive_change_interval']:
                            enemy.direction = Vector2(0, 0)
                        else:
                            self.evasion_start_time = current_time
                            self.evasion_duration = random.gauss(enemy.combat_config['evasive_change_interval'], enemy.combat_config['evasive_change_interval'] * 0.2)
                            self.evasive_direction = None

                elif shooting_range < distance <= notice_radius:
                    # Move towards the player with random variation
                    if self.evasion_start_time is None or self.evasion_duration is None:
                        self.evasion_start_time = current_time
                        self.evasion_duration = random.gauss(enemy.combat_config['evasive_change_interval'], enemy.combat_config['evasive_change_interval'] * 0.2)

                    elapsed_time = current_time - self.evasion_start_time

                    if elapsed_time < self.evasion_duration:
                        if self.evasive_direction is None:
                            evasive_base_direction = direction
                            random_variation = Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                            combined_direction = (evasive_base_direction + random_variation).normalize()
                            self.evasive_direction = combined_direction

                        enemy.direction = self.evasive_direction
                    else:
                        if current_time - self.evasion_start_time < enemy.combat_config['evasive_change_interval']:
                            enemy.direction = Vector2(0, 0)
                        else:
                            self.evasion_start_time = current_time
                            self.evasion_duration = random.gauss(enemy.combat_config['evasive_change_interval'], enemy.combat_config['evasive_change_interval'] * 0.2)
                            self.evasive_direction = None

            enemy.status = 'move'
        else:
            enemy.direction = Vector2(0, 0)

        # print(f"in move mixed strat")
        # print(f"status : {enemy.status}")
        # print(f"direction : {enemy.direction}")