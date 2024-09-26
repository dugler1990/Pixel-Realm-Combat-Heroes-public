import random
from AnimatedEnvironmentSprite import AnimatedEnvironmentSprite

class WaterTile(AnimatedEnvironmentSprite):
    def __init__(self, pos, groups, animation_config, speed=100, adjacent_tiles=None):
        super().__init__(pos, groups, animation_config['mild_ripple_neutral'], speed)
        self.animation_config = animation_config
        self.adjacent_tiles = adjacent_tiles  # Dictionary of neighboring WaterTiles
        self.current_state = 'calm'
    def adjust_frames_for_wind(self, wind_direction, wind_intensity):
        wind_intensity = wind_intensity + abs( random.gauss(0,float(1.5)) )
        # Determine ripple intensity based on wind
        if wind_intensity < 5:
            new_state = 'calm'
        elif wind_intensity < 10 and wind_intensity >= 5:
            # Adjust ripple based on wind direction, treat close to 0° or 180° as neutral
            if (0 <= wind_direction < 45) or (315 < wind_direction <= 360) or (135 < wind_direction < 225):
                new_state = 'mild_ripple_neutral'
            elif 90 < wind_direction <= 270:
                new_state = 'calm'
            else:
                new_state = 'calm'
        elif wind_intensity >= 10:
            if 90 < wind_direction <= 270:
                new_state = 'intense_ripple_left'
            else:
                new_state = 'intense_ripple_right'

        # Random chance for waves, influenced by neighboring tiles
        if random.random() < 0.1 + 0.4 * (wind_intensity - 0.5):  
            if self.adjacent_tiles and 'left' in self.adjacent_tiles and isinstance(self.adjacent_tiles['left'], WaterTile):
                if self.adjacent_tiles['left'].current_state in ['mild_wave_right', 'intense_wave_right']:
                    new_state = 'mild_wave_right'
            if self.adjacent_tiles and 'right' in self.adjacent_tiles and isinstance(self.adjacent_tiles['right'], WaterTile):
                if self.adjacent_tiles['right'].current_state in ['mild_wave_left', 'intense_wave_left']:
                    new_state = 'mild_wave_left' 

        # Set the new animation if it's different from the current
        if new_state != self.current_state:
            self.frames = self.animation_config[new_state]
            self.frame_index = 0  
            self.current_state = new_state

    def update(self, weather,dt=None):
        self.adjust_frames_for_wind(weather.wind_direction, weather.wind_intensity)
        super().update(weather)  # Call the base update method
