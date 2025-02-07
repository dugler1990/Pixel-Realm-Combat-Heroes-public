import pygame
from Support import import_folder
from AnimatedEnvironmentSprite import AnimatedEnvironmentSprite

class Torch(AnimatedEnvironmentSprite):
    def __init__(self, pos, groups, config, speed = 100):
        # Load frames based on the provided configuration
        self.animation_config = {state: import_folder(path) for state, path in config.items()}
        initial_frames = self.animation_config['normal']  # Default to 'normal' animation
        super().__init__(pos, groups, initial_frames, speed, affected_by_wind=True)
        
        # Store current state
        self.current_state = 'normal'
        self.hitbox = self.rect.inflate(-10, -10)
        
    def adjust_frames_for_wind(self, wind_direction, wind_intensity):
        #print(f'wind_intensity  : {wind_intensity}')
        # Determine the new state based on wind direction and intensity
        pass


    def update_light(self, light_level = 1):
        # Override to adjust image brightness based on light level
        super().update_light(light_level)  # Adjust brightness of the current frame
        # You could add additional visual effects here, like shadows or highlights




    def update(self,weather):
        # Call the base update method to handle regular animation
        #print(f"ANIMATION SPEED : {self.animation_speed}")
        #print(f" frame_index : frame index {self.frame_index} , len {len(self.frames)}")
        super().update(weather)
        # Additional logic can be implemented here if needed (e.g., checking health, interaction with characters)
