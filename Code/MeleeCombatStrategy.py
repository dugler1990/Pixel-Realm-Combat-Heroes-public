import pygame
import random
from combat_strategy_interface import CombatStrategy



class MeleeCombatStrategy(CombatStrategy):
    def __init__(self, parry_effects=None, movement_behavior="towards"):
        self.parry_effects = parry_effects or {}
        self.movement_behavior = movement_behavior

    def decide_action(self, enemy, player):
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.melee_attack_radius and enemy.can_attack:
            enemy.current_attack_type = "melee"
        else:
            enemy.current_attack_type = None

    def execute_attack(self, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_action_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "melee":
                # Choose a melee attack type if there are multiple
                attack = random.choice(enemy.melee_attacks) if hasattr(enemy, 'melee_attacks') else enemy.attack_damage
                enemy.damage_player(attack, "melee")
                enemy.attack_sound.play()
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        
        if self.movement_behavior == "towards":
            if distance <= enemy.melee_attack_radius and enemy.can_attack:
                enemy.status = "attack"
            elif distance <= enemy.notice_radius:
                enemy.status = "move"
                enemy.direction = direction
            else:
                enemy.status = "idle"
        elif self.movement_behavior == "away":
            if distance <= enemy.notice_radius:
                enemy.status = "move"
                enemy.direction = -direction
            else:
                enemy.status = "idle"

    def parry(self, enemy, player):
        if enemy.current_attack_type == "melee":
            if random.random() < enemy.parry_chance:
                enemy.parry_sound.play()
                enemy.can_attack = False
                pygame.time.set_timer(enemy.parry_cooldown_event, enemy.parry_cooldown)
                
                # Apply configured parry effects
                effect = self.parry_effects.get('melee', {})
                if 'status' in effect:
                    player.status = effect['status']
                    if effect['status'] == "stunned":
                        player.stun_duration = effect.get('duration', 1000)
                        player.stun_start_time = pygame.time.get_ticks()
                if 'knockback' in effect:
                    knockback_distance = effect['knockback']
                    player.rect.x += enemy.direction.x * knockback_distance
                    player.rect.y += enemy.direction.y * knockback_distance
