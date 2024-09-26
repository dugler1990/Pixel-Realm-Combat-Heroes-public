import pygame
import random
from AnimatedEnvironmentSprite import AnimatedEnvironmentSprite
from Settings import *
class WaterTile(AnimatedEnvironmentSprite):
    def __init__(self,
                 pos,
                 groups,
                 animation_config,
                 base_speed=40,
                 min_speed=20,
                 max_speed=150, 
                 index=(0, 0),
                 adjacent_tiles=None,
                 
                 ):
        
        super().__init__(pos, groups, animation_config['calm'], base_speed)
        self.animation_config = animation_config
        self.base_speed = base_speed
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.index = index  # Position index in the grid
        self.current_state = 'calm'
        self.last_speed_update_time = 0
        self.speed_update_frequency = 5000  # Base frequency for speed changes
        self.adjacent_tiles = adjacent_tiles 
        self.speed = base_speed
        self.TILESIZE = TILESIZE
        self.scale_animation()
    
     
    def scale_animation(self):
        if self.TILESIZE:
            for state, frames in self.animation_config.items():
                for i, frame in enumerate(frames):
                    self.animation_config[state][i] = pygame.transform.scale(frame, (self.TILESIZE, self.TILESIZE))
    
    def randomize_speed(self, wind_intensity):
        intensity_factor = max(1, wind_intensity / 5)  # Scale factor based on wind intensity
        speed_variation = random.randint(-80, 80) * self.speed // 100

        # Compute the average speed of adjacent tiles
        neighbor_speeds = [tile.speed for tile in self.adjacent_tiles.values() if tile is not None]
        if neighbor_speeds:
            average_neighbor_speed = sum(neighbor_speeds) / len(neighbor_speeds)
            new_speed = (self.speed + speed_variation * intensity_factor + (average_neighbor_speed/4)) // float(1.25)
        else:
            new_speed = self.speed + speed_variation * intensity_factor

        new_speed = max(self.min_speed, min(new_speed, self.max_speed))
        return new_speed
    
    def adjust_speed_periodically(self, wind_intensity):
        current_time = pygame.time.get_ticks()
        # Frequency of speed updates inversely related to wind intensity
        update_frequency = self.speed_update_frequency / max(1, wind_intensity / 5)
        if current_time > self.last_speed_update_time + update_frequency:
            self.speed = self.randomize_speed(wind_intensity)
            self.last_speed_update_time = current_time


    def determine_state_based_on_wind(self, wind_direction, wind_intensity):
        if wind_intensity < 5:
            return 'calm'
        elif wind_intensity < 10:
            return 'mild_ripple_neutral'
        else:
            if 90 < wind_direction <= 270:
                return 'intense_ripple_left'
            else:
                return 'intense_ripple_right'
        
        # Random chance for waves, influenced by neighboring tiles
        if random.random() < 0.1 + 0.4 * (wind_intensity - 0.5):  # Increase chance with wind intensity
            if self.adjacent_tiles and 'left' in self.adjacent_tiles and isinstance(self.adjacent_tiles['left'], WaterTile):
                if self.adjacent_tiles['left'].current_state in ['mild_wave_right', 'intense_wave_right']:
                    new_state = 'mild_wave_right'  # Wave propagation from left to right
            if self.adjacent_tiles and 'right' in self.adjacent_tiles and isinstance(self.adjacent_tiles['right'], WaterTile):
                if self.adjacent_tiles['right'].current_state in ['mild_wave_left', 'intense_wave_left']:
                    new_state = 'mild_wave_left'  # Wave propagation from right to left



    def adjust_frames_for_wind(self, wind_direction, wind_intensity):
        if wind_direction <= 180:  # Wind blowing from left to right
            wind_delay = self.index[0] * 10  # Delay increases with x index
        else:  # Wind blowing from right to left
            wind_delay = (len(self.index) - self.index[0]) * 10  # max_x_index based on grid size

        current_time = pygame.time.get_ticks()
        if current_time > self.last_speed_update_time + wind_delay:
            new_state = self.determine_state_based_on_wind(wind_direction, wind_intensity)
            if new_state != self.current_state:
                self.frames = self.animation_config[new_state]
                self.frame_index = 0
                self.current_state = new_state
            self.last_wind_update_time = current_time

    def update(self, weather, dt=None):
        super().update(weather,dt)
        if type(weather) != float:
            if weather:
                self.adjust_speed_periodically(weather.wind_intensity)  # Adjust speed dynamically based on wind
                self.adjust_frames_for_wind(weather.wind_direction, weather.wind_intensity)
