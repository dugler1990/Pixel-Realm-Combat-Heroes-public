import random
from pygame import Vector2
import pygame
from functools import partial
import math
from Settings import TILESIZE




def in_range_of_player(enemy, player, radius):
    distance = Vector2(enemy.rect.center).distance_to(Vector2(player.rect.center))
    return distance <= radius


def health_below_threshold(enemy, player, threshold):
    return enemy.health <= threshold

def create_trigger_condition(trigger_config):
    name = trigger_config['name']
    parameters = trigger_config.get('parameters', {})

    if name == 'in_range_of_player':
        radius = parameters.get('radius', 100)
        return partial(in_range_of_player, radius=radius)
    elif name == 'health_below_threshold':
        threshold = parameters.get('threshold', 50)
        return partial(health_below_threshold, threshold=threshold)
    else:
        raise ValueError(f"Unknown trigger condition name: {name}")





def create_special_attack(attack_config):
    name = attack_config['name']
    cooldown = attack_config['cooldown']
    cooldown_variability = attack_config['cooldown_variability']
    trigger_conditions = attack_config.get('trigger_conditions', [])  # Now a list of dicts
    chance = attack_config.get('chance', 1) 

    if name == 'Teleport':
        #print("detected Teleport")
        max_distance = attack_config['max_distance']
        return TeleportAttack(cooldown, cooldown_variability, trigger_conditions, max_distance, chance)
    elif name == 'MultiShotIceball':
        num_shots = attack_config['num_shots']
        projectile_type = attack_config['projectile_type']
        return MultiShotIceball(cooldown, cooldown_variability, trigger_conditions, num_shots, projectile_type,chance)
    elif name == 'SummonIceGhosts':
        spawn_radius = attack_config['spawn_radius']
        cast_time = attack_config['cast_time']
        damage_threshold = attack_config['damage_threshold']
        return SummonIceGhosts(cooldown,
                               cooldown_variability,
                               trigger_conditions,
                               spawn_radius,
                               cast_time,
                               damage_threshold,
                               chance)
    else:
        raise ValueError(f"Unknown special attack name: {name}")







class SpecialAttack:
    def __init__(self, name, cooldown, cooldown_variability, trigger_conditions):
        self.name = name
        self.base_cooldown = cooldown
        self.cooldown_variability = cooldown_variability
        self.trigger_conditions = [create_trigger_condition(cond) for cond in trigger_conditions]
        #print(f"trigger conditions created:{self.trigger_conditions}")
        self.last_used_time = 0

    def execute(self, enemy, player, context):
        raise NotImplementedError

    def is_ready(self, current_time):
        return current_time - self.last_used_time >= self.base_cooldown + random.uniform(-self.cooldown_variability, self.cooldown_variability)


    def can_trigger(self, enemy, player):
        return all(cond(enemy, player) for cond in self.trigger_conditions)

class TeleportAttack(SpecialAttack):
    def __init__(self, cooldown, cooldown_variability, trigger_condition, max_distance, chance):
        super().__init__('Teleport', cooldown, cooldown_variability, trigger_condition)
        self.max_distance = max_distance
        self.chance = chance
        
    def execute(self, enemy, player, context):
        #print(f"executing teleport !!")
        if random.random() < self.chance:# TODO: make this a function of the Special attack they all have it
            direction_vector = Vector2(enemy.rect.center) - Vector2(player.rect.center)
            if direction_vector.length() > 0:
                direction_vector.normalize_ip()
                teleport_position = Vector2(player.rect.center) + direction_vector * self.max_distance * random.gauss(0.90,0.03)
                enemy.rect.center = teleport_position
                enemy.hitbox.center = teleport_position
                enemy.status = 'Teleport'
            self.last_used_time = pygame.time.get_ticks()

class MultiShotIceball(SpecialAttack):
    def __init__(self,
                 cooldown,
                 cooldown_variability,
                 trigger_condition,
                 num_shots,
                 projectile_type,
                 chance):
        super().__init__('MultiShotIceball', cooldown, cooldown_variability, trigger_condition)
        self.num_shots = num_shots
        self.projectile_type = projectile_type
        self.chance = chance

    def execute(self, enemy, player, context):
        if random.random() < self.chance:
            for _ in range(self.num_shots):
                random_direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                
                
                context["fire_projectile"]( enemy_pos = enemy.rect.center,
                                            target_pos = enemy.rect.center + random_direction * 50,
                                            projectile_type = self.projectile_type,
                                            groups = enemy.groups)
            enemy.status = 'MultiShotIceball'
            self.last_used_time = pygame.time.get_ticks()
            
            
class SummonIceGhosts(SpecialAttack):
    def __init__(self, cooldown, cooldown_variability, trigger_condition, spawn_radius, cast_time, damage_threshold, chance):
        super().__init__('SummonIceGhosts', cooldown, cooldown_variability, trigger_condition)
        self.spawn_radius = spawn_radius
        self.cast_time = cast_time
        self.damage_threshold = damage_threshold
        self.is_casting = False
        self.cast_start_time = None
        self.starting_health = 0
        self.chance = chance

    def execute(self, enemy, player, context):
        if random.random() < self.chance:
            self.is_casting = True
            self.cast_start_time = pygame.time.get_ticks()
            self.starting_health = enemy.health  # Capture the health at the start of casting
            
            enemy.status = 'Summoning'

    def update(self, enemy, player, context):
        if not self.is_casting:
            return

        current_time = pygame.time.get_ticks()
        print(f"udpate : current:{current_time}  start :{self.cast_start_time} cast_time = {self.cast_time}")
        if current_time - self.cast_start_time >= self.cast_time:
            damage_taken_during_cast = self.starting_health - enemy.health
            print(f"damage taken : {damage_taken_during_cast}, thresh: {self.damage_threshold}")
            if damage_taken_during_cast < self.damage_threshold:
                num_ghosts_to_spawn = 3  # You can adjust this number as needed
                for _ in range(num_ghosts_to_spawn):
                    
                    spawn_pos = self.generate_random_position(enemy.rect.center, self.spawn_radius)
                    print(f"spawn pos  : {spawn_pos}")
                    context["spawn_enemy"](config = {'type': 'ice_ghost'},
                                        pos = spawn_pos)
                    print("supposidly spawned ghost")
            self.is_casting = False
            enemy.status = 'idle'
            self.last_used_time = current_time
        else:
            # Check if the damage threshold is exceeded during casting
            damage_taken_during_cast = self.starting_health - enemy.health
            if damage_taken_during_cast >= self.damage_threshold:
                self.is_casting = False
                enemy.status = 'idle'

    def generate_random_position(self, center, radius):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)/TILESIZE
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance
        return (center[0]/TILESIZE + offset_x, center[1]/TILESIZE + offset_y)
