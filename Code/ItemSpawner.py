import pygame
import random
import json
from Item import Item  # Assume this is your Item class
from Settings import TILESIZE

class ItemSpawner:
    def __init__(self):
        
        self.items = []  # used only for farmed items atm.
        self.spawned_positions = {}
        

    def load_item_mapping(self, standard_objects_path):
        """Load item ID to configuration mapping from a JSON file."""
        with open(standard_objects_path, 'r') as file:
            standard_item_configs = json.load(file)
        self.item_mapping = {item['item_id']: item for item in standard_item_configs}
        

    def load_item_config(self, item_config_path):
        """Load item configurations from a JSON file."""
        with open(item_config_path, 'r') as file:
            self.item_configs = json.load(file)


    def spawn_fixed_items(self):
        fixed_items = []
        for config in self.item_configs:
            if config.get('spawn_type') == 'fixed':
                for position in config['positions']:  # Iterate over positions
                    item = self.create_item(config, position)
                    fixed_items.append(item)
        return fixed_items




    def drop_from_enemy(self, enemy):
        """Drop items from an enemy based on defined drop logic."""
        #print('In drop from enemy')
        #print(dir(enemy))
        dropped_items = []
        if hasattr(enemy, 'item_drop_info'):
            drop_info = enemy.item_drop_info
            #print('has item drop info')
            # Handle guaranteed drops
            for drop in drop_info.get('guaranteed_drops', []):
                item_id = drop['item_id']
                quantity = drop.get('quantity', 1)
                for _ in range(quantity):

                    drop_config = self.item_mapping.get(item_id)

                    #print(enemy.rect.bottomright)
                    #print(enemy.rect.bottomright[0])
                    
                    #print(drop_config['position'])
                   
                    drop_config['positions'].append([enemy.rect.bottomright[0], enemy.rect.bottomright[1]]) # Not sure that this is necessary now, we pass the positions directly to the item creation
                    position = [enemy.rect.bottomright[0], enemy.rect.bottomright[1]] # to pass directly to create_item

                    #print(drop_config)
                    item = self.create_item( drop_config, position )
                    dropped_items.append(item)
            # Handle random drops
            if drop_info.get('random_drop_logic') == 'single':
                # Only one item from the random drop list can be chosen
                total_chance = sum(drop['chance'] for drop in drop_info['random_drop_list'])
                random_chance = random.random() * total_chance
                cumulative_chance = 0
                for drop in drop_info['random_drop_list']:
                    cumulative_chance += drop['chance']
                    if random_chance <= cumulative_chance:
                         
                        # WL HERE : 
                        drop_config = self.item_mapping.get(drop['item_id'])
                        drop_config['positions'].append([enemy.rect.bottomright[0], enemy.rect.bottomright[1]])
                        position = [enemy.rect.bottomright[0], enemy.rect.bottomright[1]] 
                        item = self.create_item(drop_config, position)
                        dropped_items.append(item)
                        break
            return dropped_items


#### Not  currently in use
    def respawn_items(self):
        """Respawn items that continuously appear at certain locations."""
        for item_config in self.item_configs:
            #print(f"item config: {item_config}")
            item_key = item_config.get("item_id")
            
            if item_config.get('spawn_type') == 'respawn':
                for position in item_config.get('positions', []):  # Ensure it iterates over positions
                    if random.random() <= item_config.get('respawn_rate', 0):
                        item_instance = self.create_item(item_config, position)  # Create a new item instance for each position
                        # Handle adding the visual representation of the item_instance to the game
            if item_config.get('spawn_type') == 'farmed_item':
                
                #print(f"In respawn items of type farmed_item")
                #print(f"Item config currently : {item_config}")

                for position in item_config.get('positions',[]):
                    new_item = self.create_item(item_config,position)
                    self.items.append(new_item)
                    #print( f"self . items : {self.items}" )

    def update_spawn_positions(self, item_id, new_positions):
        """Updates the spawn positions for a given item_id, ensuring no duplicates."""
        
        #print(f"updating spawn items using :{new_positions}")
        #print(f"old items : {self.items}")
        for new_position in new_positions:
            #print(f"new_position:{new_position}")
            if item_id not in self.spawned_positions:
                #print("item not in spawned_positions currently...")
                self.spawned_positions[item_id] = set()

            #print(f"\n\nspawned positions: {self.spawned_positions}\n\n")

            if tuple(new_position) not in self.spawned_positions[item_id]:
                #print("position for this item does not previously exist")
                # This is a new position for the item
                self.spawned_positions[item_id].add(tuple(new_position))
                # Create the item as it's a new position
                item_config = self.item_mapping[item_id]  # Assuming item_mapping is {item_id: item_config}
                item = self.create_item(item_config, new_position)
                self.items.append(item)
        #print(f"new items : {self.items}")

    def spawn_from_chest(self, chest_position):
        """Spawn one or more items when a chest is opened."""
        for item_key, config in self.item_configs.items():
            if config.get('spawn_type') == 'chest':
                for _ in range(random.randint(1, config.get('max_items', 1))):
                    self.create_item(item_key, chest_position)


    def create_item(self, item_config, position):
        """Create and return an Item instance."""
        #position[0] = position[0] * TILESIZE
        #position[1] = position[1] * TILESIZE
        ############### CHANGE FOR NO SCALING IN INIT:

        #print(f"creating item : {item_config}")
        #print(f"position:{position}")

            # Extracting parameters with default values if not present in item_config
        float_offset = item_config.get('float_offset', 0)  # Default value is 0 if 'float_offset' is not in item_config
        float_speed = item_config.get('float_speed', 0.5)  # Default value is 0.5 if 'float_speed' is not in item_config
        float_direction = item_config.get('float_direction', 1)  # Default value is 1 if 'float_direction' is not in item_config
        float_amplitude = item_config.get("float_amplitude",5)
        
        
        #print(f" CReATED ITEM : {item_config}")
        
        return Item(item_config['image_path'],
                     position,
                     item_config['item_id'],
                     item_config['effect'],
                     item_config['effect_type'],
                     float_offset=float_offset,
                     float_speed=float_speed,
                     float_direction=float_direction,
                     float_amplitude = float_amplitude
                     )

    def update(self):
        """Update method for respawning items and other time-based spawning logic."""
        #self.respawn_items()
        #print(f"  \n \n RETURNED ITEMS IN UPDATE : {self.items}")
        items_to_spawn = self.items
        self.items = []
        return items_to_spawn
      
    def remove_item(self, item):
        """Removes an item and marks its position as available."""
        if item in self.items:
            self.items.remove(item)
            item_pos = (item.position[0] // TILESIZE, item.position[1] // TILESIZE)
            # Assuming each item has a unique ID, find the item_id by item
            item_id = next((id for id, config in self.item_mapping.items() if config == item.config), None)
            if item_id and item_pos in self.spawned_positions.get(item_id, set()):
                self.spawned_positions[item_id].remove(item_pos)

