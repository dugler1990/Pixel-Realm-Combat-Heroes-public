import json
import random
import pygame
from Enemy import Enemy  # Make sure to import your Enemy class
from Settings import TILESIZE 
from random import randint
from Eskimo import Eskimo
from IceClone import IceClone
from Trap import Trap
from PolarBear import PolarBear
from Settings import monster_data
import SpecialAttacks
import math

CHARACTER_CLASSES = {
    'eskimo': Eskimo,
    'polarbear':PolarBear
    # Add other neutral character classes here as you create them.
}

class Spawner:
    def __init__(self, level, persistent_enemy_data, fire_projectile):# could do better way to access all level call backs.
        self.level = level  # Reference to the main game class to access game state, level manager, etc.
        self.enemies = []  # List to keep track of all spawned enemies
        self.timed_spawns = {}        
        self.spawn_timers = {}  # Timers for timed enemy spawns
        self.persistent_enemy_data = persistent_enemy_data
        self.spawn_areas = [] 
        self.neutral_characters = []
        self.fire_projectile = fire_projectile

    def spawn_trap(self, trap_config):
        # Check the type of trap to spawn based on a key in the configuration, for example:
        if trap_config['class'] == IceClone:
            trap = IceClone(
                pos=trap_config['pos'],
                groups=trap_config['groups'],
                image_path=trap_config['image_path'],
                animation_player=self.level.animation_player,
                effect_type=trap_config['effect_type'],
                death_animation='ice_clone_death_1',
                add_exp=self.level.add_exp,
                target_type=trap_config.get('target_type', 'enemies'),
                trigger=trap_config.get('trigger', 'timer'),
                lifespan=trap_config.get('lifespan', 3000),
                radius=trap_config.get('radius', 5),
                health=trap_config.get('health', 100),
                exp_value=trap_config.get('exp_value', 0)
            )
            #print(trap_config)
        else:
            # Default to the general Trap class if no specific class is required
            trap = Trap(
                pos=trap_config['pos'],
                groups=trap_config['groups'],
                image_path=trap_config['image_path'],
                animation_player=self.level.animation_player,
                effect_type=trap_config['effect_type'],
                add_exp=self.level.add_exp,  # This needs to be provided from your level or game environment
                target_type=trap_config.get('target_type', 'all'),
                trigger=trap_config.get('trigger', 'timer'),
                lifespan=trap_config.get('lifespan', 5000),
                radius=trap_config.get('radius', 100),
                health=trap_config.get('health', 100),
                exp_value=trap_config.get('exp_value', 50)
            )
    
        # Adding the trap to sprite groups is handled in the Trap's __init__, so we just return the trap
        return trap

    
    def set_layout_callback_update_quad_tree(self, func):
        self.layout_callback_update_quad_tree = func

    def choose_enemy_based_on_weights(self, weights):
        total_weight = sum(weights.values())
        random_value = randint(1, total_weight)
        for enemy, weight in weights.items():
            if random_value <= weight:
                return enemy
            random_value -= weight


    def load_enemy_info(self, path):
        with open(path, 'r') as file:
            self.enemy_configs = json.load(file)

    def add_spawn_area(self, spawn_matrix, spawner_config, obj_info):
        
        
        
        
        self.spawn_areas.append({
            'matrix': spawn_matrix,
            'config': spawner_config,
            'object_info': obj_info,  # Store object info if needed for position reference
            'spawn_timer':0,
            'spawn_scale_timer':0
        })


    def handle_spawn_areas(self, player, dt):
        #current_time = pygame.time.get_ticks() # 
        #print("spawn areas:")
        #print(self.spawn_areas)
        for area in self.spawn_areas:
            
            area["spawn_scale_timer"] += dt
            area["spawn_timer"] += dt
            #print("config")
            #print(area["config"])
            if "time_scaled" in area["config"] :
                #print("timescaled bool")
                #print(area["config"]['time_scaled'])
                if area["config"]['time_scaled']:
                    if area["spawn_scale_timer"] > 10:
                        
                        # reset
                        area["spawn_scale_timer"] = 0 
                        
                        # update number of spawned items by config
                        if area["config"]["scale_type"] == "multiple":
                            area['config']["spawn_number"] *= 2
                            #print("spawn number")
                            #print(area['config']["spawn_number"])
            
            # print("SPAWN ATTEMPT")
            # print(f"area pos : {area['object_info']['x_pos']}")
            # print(f"area pos : {area['object_info']['y_pos']}")
            
            config = area['config']
            # Player proximity test, 
            proximity = config.get( "distance", 2000 )
            if isinstance(proximity, int):
                distance = math.sqrt( ( area["object_info"]["x_pos"]*TILESIZE- player.rect.center[0] )**2 + ( area["object_info"]["y_pos"]*TILESIZE - player.rect.center[1] )**2 ) 
                
                #print("distance and proximity")
                #print(distance)
                #print(proximity)
                if distance > proximity:
                    continue
                    
            #print(config['next_spawn_time'])
            #print(current_time)
            #print("printing spawn timer")
            #print(area["spawn_timer"])
            #print('frequency')
            #print(config['frequency'])
            
            if 'frequency' not in config or area["spawn_timer"]>= config['frequency']:
                area["spawn_timer"]= 0
                
                #print("len enemies :")
                #print(len(self.enemies))
                
                #print("enemies")
                #print(self.enemies)
                
                if len(self.enemies) < config['spawn_limit']:
                    
                    for i in range(config['spawn_number']):
                        spawn_pos = self.choose_random_spawn_pos(area['matrix'], area['object_info'])
                        if spawn_pos:
                            chosen_enemy = self.choose_enemy_based_on_weights(config['enemy_spawn_weights'])
                            
                            # Should get this info from standarcd dict in spawner i think easier than in each spawner config
                            if chosen_enemy == 'demon_dog':
                                special_attacks = {'projectile':'demon_dog_projectile'}
                                fire_projectile = self.fire_projectile
                                
                                ## Ok , so i'm handling this in the spawn area, lets not waste future time
                                #       this needs to be in config, 
                                #       spawners just work with enemy names
                                #       all other info is in Settings
                                #       i will use an enemy config file
                                #       for now ill just import this in Settings
                                
                                #       key goal is, i do not want this if demon dog in handle spawn areas,
                                #                     if i spawn a demon dog from initial , he will be mellee
                                #                     i could just put this in Settings RN.
                                
                                
                                
                                
                                # WL 
                                # issue is that im not doing this in initial instantiation, basically
                                # setting fire_projectile i think.
                                
                                
                                
                            else:
                                special_attacks = monster_data[chosen_enemy].get('special_attacks',None)
                                fire_projectile = self.fire_projectile
                                
                            
                            self.spawn_enemy({'type': chosen_enemy,
                                              'pos': spawn_pos,
                                              'fire_projectile':fire_projectile,
                                              'special_attacks':special_attacks})
                    
                
                #config['next_spawn_time'] = current_time + config['frequency'] from previous implementation


    def choose_random_spawn_pos(self, spawn_matrix, object_info):
        possible_positions = []
        for y, row in enumerate(spawn_matrix):
            for x, cell in enumerate(row):
                if cell == 1:
                    world_x = object_info['x_pos'] + x
                    world_y = object_info['y_pos'] + y
                    possible_positions.append((world_x, world_y))
        return random.choice(possible_positions) if possible_positions else None



    def generate_combat_context(self, level, combat_config):
        context = {}
        if 'damage_player' in combat_config.keys():# keys is not the best, its got True False atm for no reason , no biggy TODO:
            context['damage_player'] = level.damage_player
        if 'fire_projectile' in combat_config.keys():
            context['fire_projectile'] = level.fire_projectile
        if 'redirect_projectile' in combat_config.keys():
            context['redirect_projectile'] = level.redirect_projectile_callback
        if 'trigger_death_particles' in combat_config.keys():
            context['trigger_death_particles'] = level.trigger_death_particles
        if 'add_exp' in combat_config.keys():
            context['add_exp'] = level.add_exp
        if 'spawn_enemy' in combat_config.keys():
            context['spawn_enemy'] = level.spawner.spawn_enemy
        if 'update_quad_tree' in combat_config.keys():
            context['update_quad_tree'] = level.layout_manager.add_obstacle_sprite_to_quad_tree
        if 'spawn_enemy' in combat_config.keys():
            context['spawn_enemy'] = self.spawn_enemy
                
        # Add other methods as needed based on combat_config
        return context


    def spawn_enemy(self, config, pos=None):

        #print( f"enemy spawn attempt {config}, {pos}" )
        if not pos:  # If no position is provided, use the one from the config
            pos = config['pos']
        # Scale position by TILESIZE
        scaled_pos = (pos[0] * TILESIZE, pos[1] * TILESIZE)
        
        monster_config = monster_data[config['type']]
        #if config['type'] == 'ice_mage':
            #print("monster_config in spawner for icemage")
            #print(monster_config)
        
        combat_config = monster_config.get('combat_config', {})
        #if config['type'] == 'ice_mage':
            #print("combat_config in spawner for icemage")
            #print(combat_config)
        combat_context = combat_config.get('combat_context', {})
        
        #if config['type'] == 'ice_mage':
            #print("combat_context in spawner for icemage")
            #print(combat_context)
        
        combat_context = self.generate_combat_context(self.level, combat_context)
        
        #if config['type'] == 'ice_mage':
            #print("final combat_config in spawner for icemage")
            #print(combat_context)
        
        # Create special attacks based on the configuration
        special_attacks_config = combat_config.get('special_attacks', [])
        special_attacks = [SpecialAttacks.create_special_attack(attack) for attack in special_attacks_config]

        #if config['type'] == 'ice_mage':
           # print("special attacks config")
            #print(special_attacks_config)
            #print(special_attacks)

        
## TODO: the level is passed to the spawner.... should this use callbacks ? hmm
        enemy = Enemy(  monster_name=config['type'], 
                        pos=scaled_pos,
                        groups=[self.level.layout_manager.visible_sprites, self.level.attackable_sprites],
                        obstacle_sprites=self.level.layout_manager.obstacle_sprites,
                        combat_context=combat_context,
                        special_attacks=special_attacks,
                        persistent=config.get('persistent', False),
                        item_drop_info=config.get('item_drop_info',None) )
        self.enemies.append(enemy)
        

 

    def spawn_neutral(self, config, pos=None):
        #print(f"neutral spawn attempt {config}, {pos}")
        if not pos:  # If no position is provided, use the one from the config
            pos = config['pos']
        # Scale position by TILESIZE
        scaled_pos = (pos[0] * TILESIZE, pos[1] * TILESIZE)

        char_type = config['type']
        #print(char_type)
        char_class = CHARACTER_CLASSES.get(char_type)

        if char_class:
            # Instantiate the neutral character with the necessary sprite groups and callbacks
            neutral_character = char_class(
                pos=scaled_pos,
                groups=[self.level.layout_manager.visible_sprites, self.level.attackable_sprites],
                obstacle_sprites=self.level.layout_manager.obstacle_sprites,
                get_tile_valid_actions_callback=self.level.get_tile_valid_actions,  # Confusing bcoz this is the only place this is used and written in level
                update_item_spawner_callback=self.level.item_spawner.update_spawn_positions,  # You need to define this callback in your level class
                update_tile_image_callback=self.level.layout_manager.update_tile_image, 
                trigger_death_particles = self.level.trigger_death_particles,# You need to define this callback in your level class
                layout_callback_update_quad_tree = self.layout_callback_update_quad_tree,
                **config['attributes']
             )
            self.neutral_characters.append(neutral_character)
        else:
            print(f"Unknown neutral character type: {char_type}")


    def update(self, current_layout):
        self.handle_timed_spawns()
        self.spawn_random_enemies(current_layout)
        self.manage_persistent_enemies(current_layout)

    def handle_timed_spawns(self):
        current_time = pygame.time.get_ticks()
        for config in self.enemy_configs:
            if config.get('spawn_mode') == 'timed' and current_time > self.spawn_timers.get(config['type'], 0):
                self.spawn_enemy(config)
                self.spawn_timers[config['type']] = current_time + config['spawn_interval']

    def spawn_random_enemies(self, current_layout):
        for config in self.enemy_configs:
            if config.get('spawn_mode') == 'random' and config.get('layout') == current_layout:
                if random.random() < config.get('spawn_chance', 0.01):  # Adjust spawn chance as needed
                    self.spawn_enemy(config)

   
    
    def restore_persistent_enemies(self, layout_path):
        if layout_path in self.persistent_enemy_data:
            for enemy_state in self.persistent_enemy_data[layout_path]:
                # Reinitialize the enemy based on the saved state
                enemy = Enemy(
                    enemy_state['type'],
                    enemy_state['position'],
                    [self.level.layout_manager.visible_sprites, self.level.attackable_sprites],
                    self.level.layout_manager.obstacle_sprites,
                    self.level.damage_player,
                    self.level.trigger_death_particles,
                    self.level.add_exp,
                    persistent=True
                )
                enemy.health = enemy_state['health']  # Restore the health state
                self.enemies.append(enemy)


    def track_enemy_layouts(self):
        for enemy in self.enemies:
            if enemy.can_follow:
                # Update the enemy's last known layout and position
                enemy.last_known_layout = self.level.current_layout
                enemy.last_known_pos = (enemy.rect.x, enemy.rect.y)


    
    def on_layout_change(self, layout_path):
        # Load the current layout's enemy configurations
        enemy_config_path = os.path.join(layout_path, "enemies.json")
        with open(enemy_config_path, 'r') as file:
            current_layout_enemies = json.load(file)

        # Iterate through current layout enemies and check against tracked persistent enemies
        for enemy_config in current_layout_enemies:
            enemy_key = self.generate_enemy_key(enemy_config)  # A unique identifier for each enemy type and position

            if enemy_key in self.persistent_enemies:
                # Restore the enemy state if it's marked as persistent and not killed
                persisted_enemy = self.persistent_enemies[enemy_key]
                if not persisted_enemy['killed']:
                    self.restore_enemy(persisted_enemy)
                continue

            # Spawn new enemies if not persistent or previously killed
            self.spawn_enemy(enemy_config)

    def on_layout_update(self):
        current_time = pygame.time.get_ticks()

       # Handle timed enemy spawns
        for enemy_key, spawn_data in self.timed_spawns.items():
            if current_time >= spawn_data['next_spawn_time']:
                self.spawn_enemy(spawn_data['config'])
                spawn_data['next_spawn_time'] += spawn_data['interval']

        # Handle conditional spawns (example: based on player position)
        # This could include checking player's position and spawning enemies accordingly
