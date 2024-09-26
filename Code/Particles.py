import pygame
from Support import import_folder
from random import choice
import os
from Settings import *
from hashRect import HashableRect


# This is for file (images specifically) importing (This line changes the directory to where the project is saved)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            
            # Evasion particles
            "slide_right": import_folder("../Graphics/Particles/slide_right"),
            "slide_left": import_folder("../Graphics/Particles/slide_left"),
            
            # Trap Particles
            "freeze":import_folder("../Graphics/Traps/freeze/activate"),
            "ice_clone_death_1":import_folder("../Graphics/Traps/freeze/destroy"),
            
			# Magic
			"flame": import_folder("../Graphics/Particles/Flame/frames"),
			"aura": import_folder("../Graphics/Particles/Aura"),
			"heal": import_folder("../Graphics/Particles/Heal/frames"),
            
            
# 			"ice_ball_up_1": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/1" ),
#             "ice_ball_up_2": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/2" ),
#             "ice_ball_up_3": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/3" ),
#             "ice_ball_up_4": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/4" ),
#             "ice_ball_up_5": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/5" ),
#             "ice_ball_up_6": import_folder( "../Graphics/Particles/Ice_Ball_Up/frames/6" ),
            
            
# 			"ice_ball_down_1": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/1" ),
#             "ice_ball_down_2": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/2" ),
#             "ice_ball_down_3": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/3" ),
#             "ice_ball_down_4": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/4" ),
#             "ice_ball_down_5": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/5" ),
#             "ice_ball_down_6": import_folder( "../Graphics/Particles/Ice_Ball_Down/frames/6" ),
            
            
# 			"ice_ball_right_1": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/1" ),
#             "ice_ball_right_2": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/2" ),
#             "ice_ball_right_3": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/3" ),
#             "ice_ball_right_4": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/4" ),
#             "ice_ball_right_5": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/5" ),
#             "ice_ball_right_6": import_folder( "../Graphics/Particles/Ice_Ball_Right/frames/6" ),
            
            
# 			"ice_ball_left_1": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/1" ),
#             "ice_ball_left_2": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/2" ),
#             "ice_ball_left_3": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/3" ),
#             "ice_ball_left_4": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/4" ),
#             "ice_ball_left_5": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/5" ),
#             "ice_ball_left_6": import_folder( "../Graphics/Particles/Ice_Ball_Left/frames/6" ),
            

            "ice_ball_up": import_folder( "../Graphics/Particles/Ice_Ball_Up_/frames" ),
            "ice_ball_left": import_folder( "../Graphics/Particles/Ice_Ball_Left_/frames" ),
            "ice_ball_right": import_folder( "../Graphics/Particles/Ice_Ball_Right_/frames" ),
            "ice_ball_down": import_folder( "../Graphics/Particles/Ice_Ball_Down_/frames" ),
            
			# Attacks 
			"claw": import_folder("../Graphics/Particles/Claw"),
			"slash": import_folder("../Graphics/Particles/Slash"),
			"sparkle": import_folder("../Graphics/Particles/Sparkle"),
			"leaf_attack": import_folder("../Graphics/Particles/leaf_attack"),
			"thunder": import_folder("../Graphics/Particles/Thunder"),
            'demon_dog_projectile': import_folder("../Graphics/Particles/Ice_Ball_Right_/frames" ),


			# Monster Deaths
			"squid": import_folder("../Graphics/Particles/smoke_orange"),
			"raccoon": import_folder("../Graphics/Particles/Raccoon"),
			"spirit": import_folder("../Graphics/Particles/Nova"),
			"bamboo": import_folder("../Graphics/Particles/Bamboo"),
			"ice_ghost": import_folder("../Graphics/Particles/ice_ghost"),
            "demon_dog": import_folder("../Graphics/Particles/ice_ghost"),
			"Eskimo": import_folder("../Graphics/Particles/ice_ghost"),
            "PolarBear": import_folder("../Graphics/Particles/ice_ghost"),
            "ice_mage": import_folder("../Graphics/Particles/ice_ghost"),
            "tribey_snake": import_folder("../Graphics/Particles/Nova"),
            "venom_plant": import_folder("../Graphics/Particles/Nova"),
            "tribey_spear": import_folder("../Graphics/Particles/smoke_orange"),
            
            
            # Leafs
			"leaf":(
				import_folder("../Graphics/Particles/Leaf1"),
				import_folder("../Graphics/Particles/Leaf2"),
				import_folder("../Graphics/Particles/Leaf3"),
				import_folder("../Graphics/Particles/Leaf4"),
				import_folder("../Graphics/Particles/Leaf5"),
				import_folder("../Graphics/Particles/Leaf6"),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf1")),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf2")),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf3")),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf4")),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf5")),
				self.reflect_images(import_folder("../Graphics/Particles/Leaf6"))
				)
			}

    def reflect_images(self, frames):
        new_frames = []

        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)
        return new_frames

    def create_grass_particles(self, pos, groups):
        animation_frames = choice(self.frames["leaf"])
        ParticleEffect(pos, animation_frames, groups)
    #@profile
    def create_particles(self, 
                         animation_type,
                         pos,
                         groups,
                         quadtree=None,
                         direction = None,
                         movement=None,
                         is_moving=False,
                         total_distance=0,
                         frame_duration=100):
        
        animation_frames = self.frames[animation_type]
        
        #print( f'PARTICLE EFFECT PARAMS  : direction:{direction}, is_moving={is_moving}, movement : {movement if is_moving else None}' )
        particle = ParticleEffect(pos=pos,
                       frames=animation_frames,
                       groups=groups,
                       direction=direction,
                       movement = movement if is_moving else None,
                       is_moving=is_moving,
                       total_distance=total_distance,
                       frame_duration=frame_duration,
                       quadtree=quadtree)

        # Register particle in the quadtree
        
        #print(f"QUADTREE in create_particles: {quadtree}")
        #print(f"PARTICLE: {animation_type}")
    
        if quadtree:
            quadtree.insert(HashableRect(rect = particle.rect,
                                         _id = id(particle),
                                                      direction = direction,
                                                      sprite_type = 'magic',
                                                      mask = None),
                                         alive = True # ?
                                         
                                         )
        return particle

class ParticleEffect(pygame.sprite.Sprite):
    #@profile
    def __init__(self, pos,
                 frames,
                 groups,
                 quadtree=None,
                 direction = None,
                 movement=None,
                 is_moving=False,
                 total_distance=0,
                 frame_duration=100):
        
        super().__init__(groups)
        self.frames = frames
        self.image = frames[0]
        
        #self.masks = convert_animations_to_masks(self.animations)
        
        self.rect = self.image.get_rect(center=pos)
        self.frame_index = 0
        self.movement = movement
        self.is_moving = is_moving
        self.total_distance = total_distance
        self.distance_moved = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = frame_duration  # Time in milliseconds between frames
        self.sprite_type = "magic"
        self.quadtree = quadtree
        self.id = id(self)
        
        
        # Calculate movement based on direction if provided
        if direction:
            #print(type(direction))
            #print(dir(direction))
            self.movement = direction # Adjust the speed as needed Maybe this is unecessary
            #print(self.movement)
            
        
        # Register particle in the quadtree
        if self.is_moving:
            #print(f"QUADTREE: {self.quadtree}")
            if self.quadtree:
                self.quadtree.insert(HashableRect(self.rect,
                                                  self.id,
                                                  self.movement,
                                                  self.sprite_type),
                                     alive = True)

            
    #@profile
    def update(self, dt=None):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.last_update = now

        if self.is_moving:
            if self.quadtree:
            # Update quadtree before moving
                self.quadtree.manager.remove(self.id)
          
            
            # Calculate movement if the particle is supposed to move
            
            #print("THIS IS THE AMOUNT ITS MEANT TO MOVE")
            #print(f'{dx},{dy}')
            self.rect.x += self.movement.x
            self.rect.y += self.movement.y
            self.distance_moved += abs(self.movement.length())
            #print(f"distance move : {self.distance_moved}")

            # Reinsert into quadtree after moving
            self.quadtree.insert(HashableRect(self.rect,
                                              self.id,
                                              self.movement,
                                              self.sprite_type),
                                 alive = True)

            
            # Stop moving and kill the sprite if it has moved the intended distance
            if self.distance_moved >= self.total_distance:
                if self.quadtree:
                    self.quadtree.manager.remove( self.id )
                self.kill()
        else:
            if self.frame_index >= len(self.frames)-1:
                if self.quadtree:
                    self.quadtree.manager.remove( self.id )    
                self.kill()