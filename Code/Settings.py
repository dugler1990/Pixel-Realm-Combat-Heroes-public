import os

# This is for file (images specifically) importing (This line changes the directory to where the project is saved)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Game setup
WIDTH = 1680
HEIGHT = 950
FPS = 20
TILESIZE = 150
HITBOX_OFFSET = {
	"player": -26,
	"object": -40,
	"grass": -10,
	"invisible": 0,
        "ground":0
	}

# UI
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = "../Graphics/Font/Joystix.ttf"
UI_FONT_SIZE = 18

# General Colors
WATER_COLOR = "#71ddee"
UI_BG_COLOR = "#222222"
UI_BORDER_COLOR = "#111111"
TEXT_COLOR = "#EEEEEE"

# UI Colors
HEALTH_COLOR = "Red"
ENERGY_COLOR = "Blue"
UI_BORDER_COLOR_ACTIVE = "Gold"

# Upgrade Menu
TEXT_COLOR_SELECTED = "#111111"
BAR_COLOR = "#EEEEEE"
BAR_COLOR_SELECTED = "#111111"
UPGRADE_BG_COLOR_SELECTED = "#EEEEEE"

# Weapons
weapon_data = {
        "unarmed": {"cooldown": 50, "damage": 5, "graphic": "../Graphics/Weapons/Unarmed/Full.png"}, 
	"sword": {"cooldown": 100, "damage": 15, "graphic": "../Graphics/Weapons/Sword/Full.png"},
	"lance": {"cooldown": 400, "damage": 30, "graphic": "../Graphics/Weapons/Lance/Full.png"},
	"axe": {"cooldown": 300, "damage": 20, "graphic": "../Graphics/Weapons/Axe/Full.png"},
	"rapier": {"cooldown": 50, "damage": 8, "graphic": "../Graphics/Weapons/Rapier/Full.png"},
	"sai": {"cooldown": 80, "damage": 10, "graphic": "../Graphics/Weapons/Sai/Full.png"}
    }

# Magic
magic_data = {
	"flame": {"strength": 5, "cost": 20, "graphic": "../Graphics/Particles/Flame/fire.png"},
	"heal": {"strength": 20, "cost": 10, "graphic": "../Graphics/Particles/Heal/heal.png"},
    "ice_ball":{ "strength":10, "cost":1,"graphic":"../Graphics/Particles/Ice_Ball_Down/ice_ball.png" }
	}

# Enemies
monster_data = {
	"squid": {"health": 100,
               "exp": 180,
               "attack_type": "melee", 
               "attack_sound": "../Audio/Attack/Slash.wav", 
               "speed": 6, 
               "resistance": 3,
               "combat_config":{
                "melee_attacks": [{"damage": 8, "cooldown": 1500}],
               "melee_attack_radius": 80, 
               "notice_radius": 360,
               
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                }
               }
               },
	"tribey_snake": {"health": 100,
               "exp": 180,
               "attack_type": "melee", 
               "attack_sound": "../Audio/Attack/Slash.wav", 
               "speed": 6, 
               "resistance": 3,
               "combat_config":{
                "melee_attacks": [{"damage": 8, "cooldown": 1500}],
               "melee_attack_radius": 80, 
               "notice_radius": 360,
               
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                }
               }
               },
    
	"raccoon": {"health": 300, 
             "exp": 300,  
             "attack_type": "melee", 
             "attack_sound": "../Audio/Attack/Claw.wav", 
             "speed": 4, 
             "resistance": 3, 
             "combat_config":{
             "melee_attacks": [{"damage": 80, "cooldown": 1500}],
             "melee_attack_radius": 120, 
             "notice_radius": 400,
             
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                }}
             },
	
    "spirit": {"health": 100,
               "exp": 200, 
               "attack_type": "melee", 
               "attack_sound": "../Audio/Attack/Fireball.wav", 
               "speed": 12, 
               "resistance": 3,
               "combat_config":{
                "melee_attacks": [{"damage": 9, "cooldown": 1000}],
               "melee_attack_radius": 60, 
               "notice_radius": 350,
                   
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                }
               }
             },
               
	"bamboo": {"health": 70,
                "exp": 150, 
                "attack_type": "melee", 
                "attack_sound": "../Audio/Attack/Slash.wav", 
                "speed": 6,
                "combat_config":{
                "melee_attacks": [{"damage": 6, "cooldown": 1000}],
                "resistance": 3, 
                "melee_attack_radius": 50, 
                "notice_radius": 300,
                
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                }
                }
            },
    # TODO: i was previously using the attack type for attack animations, 
    #       now the attack_type defines the combatstrategy subclass.
    #       the animations with attacks are setup so we should take advantage of this at some point.
    
    "ice_ghost": {
        "health": 70,
        "exp": 150,
        "attack_type": "melee",
        "attack_sound": "../Audio/Attack/Slash.wav",
        "speed": 9,
        "resistance": 3,
        "combat_config":{
        "melee_attack_radius": 50,
        "notice_radius": 2500,
        "melee_attacks": [{"damage": 6, "cooldown": 1000}],
        "ranged_attacks": [],
        "melee_parry_chance": 0.0,
        "projectile_parry_chance": 0.0,
        "parry_cooldown": 0,
        
            'combat_context':{
                'damage_player': True,
                'trigger_death_particles': True,
                'add_exp': True,
                'update_quad_tree': True
                }
        }
        },
        "tribey_spear": {
            "health": 70,
            "exp": 150,
            "attack_type": "melee",
            "attack_sound": "../Audio/Attack/Slash.wav",
            "speed": 15,
            "resistance": 3,
            "combat_config":{
            "melee_attack_radius": 50,
            "notice_radius": 2500,
            "melee_attacks": [{"damage": 6, "cooldown": 1000}],
            "ranged_attacks": [],
            "melee_parry_chance": 0.0,
            "projectile_parry_chance": 0.0,
            "parry_cooldown": 0,
            
                'combat_context':{
                    'damage_player': True,
                    'trigger_death_particles': True,
                    'add_exp': True,
                    'update_quad_tree': True
                    }
            }
        },
        "demon_dog": {
            "health": 50,
            "exp": 200,
            "attack_type": "ranged",
            "attack_sound": "../Audio/Attack/Slash.wav",
            "speed": 7,
            "resistance": 3,
            "combat_config":{
            "melee_attack_radius":0,  # TODO: just to not error out, i actually need to refine this, if he doesnt have melee attack of parry possibility, he should not have radius, 
                                      # infact, each parry, like each attack should have its own radius, 
                                      # i need to create new classes.
            "ranged_attack_radius": 350,
            "notice_radius": 400,
            "melee_attacks": [],
            "ranged_attacks": [{"type": "demon_dog_projectile", "damage": 15, "cooldown": 1500}],
            "melee_parry_chance": 0.0,
            "projectile_parry_chance": 0.0,
            "parry_cooldown": 0,
            
            'combat_context':{
                'damage_player': True,
                'fire_projectile': True,
                'trigger_death_particles': True,
                'add_exp': True,
                'update_quad_tree': True
                }
            }
        },
        "venom_plant": {
            "health": 500,
            "exp": 200,
            "attack_type": "ranged",
            "attack_sound": "../Audio/Attack/Slash.wav",
            "speed": 1,
            "resistance": 3,
            "combat_config":{
            "melee_attack_radius":0,  # TODO: just to not error out, i actually need to refine this, if he doesnt have melee attack of parry possibility, he should not have radius, 
                                      # infact, each parry, like each attack should have its own radius, 
                                      # i need to create new classes.
            "ranged_attack_radius": 350,
            "notice_radius": 400,
            "melee_attacks": [],
            "ranged_attacks": [{"type": "demon_dog_projectile", "damage": 15, "cooldown": 1500}],
            "melee_parry_chance": 0.0,
            "projectile_parry_chance": 0.0,
            "parry_cooldown": 0,
            
            'combat_context':{
                'damage_player': True,
                'fire_projectile': True,
                'trigger_death_particles': True,
                'add_exp': True,
                'update_quad_tree': True
                }
            }
        },
        "ice_mage": {
            "health": 4000,
            "exp": 200,
            "attack_type": "mixed",
            "attack_sound": "../Audio/Attack/Slash.wav",
            "speed": 7,
            "resistance": 3,
            "combat_config": {
                "special_attacks":[{"name":"Teleport",
                                    "chance":float(0.01),
                                    "cooldown":10000,
                                    "cooldown_variability":10000,
                                    "max_distance":390,
                                    "trigger_conditions":[{"name":"in_range_of_player",
                                                           "parameters":{"radius":100}}]},
                                   {"name":"MultiShotIceball",
                                                       "chance":float(0.1),
                                                       "cooldown":10000,
                                                       "cooldown_variability":10000,
                                                       "num_shots":10,
                                                       "projectile_type":"demon_dog_projectile",
                                                       "trigger_conditions":[{"name":"in_range_of_player",
                                                                              "parameters":{"radius":500}}]},
                                   
                                   
                                   {"name":"SummonIceGhosts",
                                                       "chance":float(0.1),
                                                       "cooldown":5000,
                                                       "cooldown_variability":1000,
                                                       "cast_time":2000,
                                                       "damage_threshold": 200,
                                                       "spawn_radius": 400,
                                                       "trigger_conditions":[{"name":"in_range_of_player",
                                                                              "parameters":{"radius":500}}]}],
                "melee_notice_radius": 200,
                "melee_attack_radius": 50,
                "ranged_attack_radius": 400,
                "notice_radius": 600,
                "melee_attacks": [{"damage": 15, "cooldown": 700}],
                "ranged_attacks": [{"type": "demon_dog_projectile", "damage": 15, "cooldown": 1500}],
                "melee_parry_chance": 0.5,
                "projectile_parry_chance": 0.5,
                "parry_cooldown": 1000,
                'evasive_change_interval': 500,
                'combat_context':{
                'damage_player': True,
                'fire_projectile': True,
                'redirect_projectile': True,
                'trigger_death_particles': True,
                'add_exp': True,
                'spawn_enemy': True,
                'update_quad_tree': True
                }
            }
        }
	
    }
