from combat_strategy_interface import CombatStrategy
import random
import time
import pygame

class RangedCombatStrategy(CombatStrategy):
    def __init__(self, parry_effects=None, movement_behavior="towards"):
        self.parry_effects = parry_effects or {}
        self.movement_behavior = movement_behavior

    def decide_action(self, enemy, player):
        distance, _ = enemy.get_player_distance_direction(player)
        if distance <= enemy.ranged_attack_radius and enemy.can_attack:
            enemy.current_attack_type = "ranged"
        else:
            enemy.current_attack_type = None

    def execute_attack(self, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - enemy.last_attack_action_time >= enemy.attack_action_cooldown:
            enemy.last_attack_action_time = current_time
            enemy.attack_time = current_time

            if enemy.current_attack_type == "ranged":
                # Choose a ranged attack type if there are multiple
                projectile_type = random.choice(enemy.ranged_attacks) if hasattr(enemy, 'ranged_attacks') else enemy.special_attacks.get('projectile')
                target_pos = player.rect.center
                enemy.fire_projectile(enemy.rect.center, target_pos, projectile_type, enemy.groups)
    
    def move(self, enemy, player):
        distance, direction = enemy.get_player_distance_direction(player)
        
        if self.movement_behavior == "towards":
            if distance <= enemy.ranged_attack_radius and enemy.can_attack:
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
        for projectile in enemy.detect_projectiles(enemy):
            if projectile.owner == player and enemy.rect.colliderect(projectile.rect):
                if random.random() < enemy.parry_chance:
                    projectile.direction *= -1  # Reflect projectile
                    projectile.speed *= 1.2
                    enemy.parry_sound.play()
                    
                    # Apply configured parry effects
                    effect = self.parry_effects.get('ranged', {})
                    if 'status' in effect:
                        player.status = effect['status']
                        if effect['status'] == "stunned":
                            player.stun_duration = effect.get('duration', 1000)
                            player.stun_start_time = pygame.time.get_ticks()
                    return True
        return False
