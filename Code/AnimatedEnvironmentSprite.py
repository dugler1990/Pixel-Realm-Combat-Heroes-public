import pygame
from Support import import_folder

class AnimatedEnvironmentSprite(pygame.sprite.Sprite):
    def __init__(self, pos, groups, initial_frames, speed, affected_by_wind=True):
        super().__init__(groups)
        
        self.frames = initial_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = self.rect.center
        self.frame_index = 0
        self.animation_speed = speed
        self.last_update = pygame.time.get_ticks()
        self.affected_by_wind = affected_by_wind
        self.previous_wind_intensity = 0
        self.previous_light_level = 1  # Assume starting during the day
        self.wind_intensity_threshold = 1  # Threshold for wind intensity change to update
        self.light_level_threshold = 0.1  # Threshold for light level change to update

    def react_to_wind(self, wind_direction, wind_intensity):
        if self.affected_by_wind and abs(wind_intensity - self.previous_wind_intensity) > self.wind_intensity_threshold:
            # Change the behavior or frames based on wind intensity
            self.adjust_frames_for_wind( wind_direction, wind_intensity)
            self.previous_wind_intensity = wind_intensity

    def adjust_frames_for_wind(self, wind_direction, wind_intensity):
        # Placeholder for how frames change with wind, to be overridden by subclasses
        pass

    def update_light(self, light_level):
        if abs(light_level - self.previous_light_level) > self.light_level_threshold:
            # Adjust brightness based on light level
            original_image = self.frames[self.frame_index]
            faded_image = pygame.Surface(original_image.get_size(), pygame.SRCALPHA)
            faded_image.fill((255 * light_level, 255 * light_level, 255 * light_level, 255), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = original_image.copy()
            self.image.blit(faded_image, (0, 0))
            self.previous_light_level = light_level

    def update(self, weather, dt = None):
        super().update()
        #print(weather)
        self.update_animations_with_weather(weather)
        now = pygame.time.get_ticks()
        
        #print(f"ANIMATION SPEED : {self.animation_speed}")
        #print(f" frame_index : frame index {self.frame_index} , len {len(self.frames)}")
        if now - self.last_update > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.last_update = now

    def update_animations_with_weather(self, weather):
        if hasattr(weather,"light_intensity"): #### TODO : this is a mess from just passing None into the weather as opposed to having it able to deal with 
                                                          # no weather area, need to work on the weather object particularly when there is no weather.
            self.update_light(weather.light_level)
        if type(weather) != float :   
            if weather:
                self.react_to_wind(weather.wind_direction, weather.wind_intensity)
