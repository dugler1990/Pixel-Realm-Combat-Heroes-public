import random
import pygame
from pygame.math import Vector2
from  hashRect import HashableRect



class CombatStrategy:
    def __init__(self, parry_effects, movement_behavior, redirect_projectile_callback):
        self.parry_effects = parry_effects
        self.movement_behavior = movement_behavior
        self.redirect_projectile_callback = redirect_projectile_callback

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
            if Vector2(projectile_rect.rect.center).distance_to(enemy.rect.center) < enemy.attack_radius:
                if random.random() < self.parry_effects['projectile_parry_chance']:
                    direction_vector = Vector2(player.rect.center) - Vector2(projectile_rect.rect.center)
                    direction_vector.normalize_ip()
                    self.redirect_projectile_callback(projectile_rect.id, direction_vector)
                    enemy.last_parry_time = current_time


class MeleeCombatStrategy(CombatStrategy):
    def __init__(self, melee_attacks, parry_effects, movement_behavior,redirect_projectile_callback):
        super().__init__(parry_effects, movement_behavior,redirect_projectile_callback)
        self.melee_attacks = melee_attacks

    def decide_action(self, enemy, player):
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.attack_radius and enemy.can_attack:
            enemy.current_attack_type = "melee"
            enemy.movement_state = 'offensive'
        else:
            enemy.current_attack_type = None
            enemy.movement_state = 'offensive'

    def execute_attack(self, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "melee":
                attack = random.choice(self.melee_attacks)
                enemy.damage_player(attack['damage'], "melee")
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        if enemy.movement_state == 'offensive':
            enemy.direction = direction
        elif enemy.movement_state == 'defensive':
            enemy.direction = -direction
        elif enemy.movement_state == 'evasive':
            enemy.direction = -direction + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        enemy.status = 'move'


class RangedCombatStrategy(CombatStrategy):
    def __init__(self, ranged_attacks, parry_effects, movement_behavior,redirect_projectile_callback):
        super().__init__(parry_effects, movement_behavior,redirect_projectile_callback)
        self.ranged_attacks = ranged_attacks

    def decide_action(self, enemy, player):
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.attack_radius and enemy.can_attack:
            enemy.current_attack_type = "ranged"
            enemy.movement_state = 'defensive'
        else:
            enemy.current_attack_type = None
            enemy.movement_state = 'defensive'

    def execute_attack(self, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "ranged":
                attack = random.choice(self.ranged_attacks)
                enemy.special_attacks[attack['type']](enemy, player)
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        if enemy.movement_state == 'defensive':
            enemy.direction = -direction
        elif enemy.movement_state == 'evasive':
            enemy.direction = -direction + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        enemy.status = 'move'


class MixedCombatStrategy(CombatStrategy):
    def __init__(self, melee_attacks, ranged_attacks, parry_effects, movement_behavior,redirect_projectile_callback):
        super().__init__(parry_effects, movement_behavior,redirect_projectile_callback)
        self.melee_attacks = melee_attacks
        self.ranged_attacks = ranged_attacks

    def decide_action(self, enemy, player):
        
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.melee_attack_radius and enemy.can_attack:
            enemy.current_attack_type = "melee"
            enemy.movement_state = 'offensive'
        elif distance <= enemy.attack_radius and enemy.can_attack:
            enemy.current_attack_type = "ranged"
            enemy.movement_state = 'defensive'
        else:
            enemy.current_attack_type = None
            enemy.movement_state = 'evasive'

        print(f"in decide actions mixed strat")
        print(f"movement state : {enemy.movement_state}")
        print(f"attack type : {enemy.current_attack_type}")

    def execute_attack(self, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "melee":
                attack = random.choice(self.melee_attacks)
                enemy.damage_player(attack['damage'], "melee")
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
            elif enemy.current_attack_type == "ranged":
                attack = random.choice(self.ranged_attacks)
                enemy.special_attacks[attack['type']](enemy, player)
                enemy.attack_sound.play()
                enemy.attack_cooldown = attack['cooldown']
                
        
        print(f"in execute attack mixed strat")
        print(f"attack : {attack}")
        print(f"special attacks : {enemy.special_attacks}")
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        if enemy.movement_state == 'offensive':
            enemy.direction = direction
        elif enemy.movement_state == 'defensive':
            enemy.direction = -direction
        elif enemy.movement_state == 'evasive':
            enemy.direction = -direction + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        enemy.status = 'move'

        print(f"in move mixed strat")
        print(f"status : {enemy.status}")
        print(f"direction : {enemy.direction}")