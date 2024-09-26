from Support import *
from Settings import *

class WeatherOverlay:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.weather_type = None
        self.current_animation = []
        self.current_frame_index = 0
        self.frame_duration = 100  # milliseconds per frame
        self.last_frame_update_time = pygame.time.get_ticks()
        self.weather_animations = {
            'rain_left': {
                1: import_folder( path = "../Graphics/Weather/Rain/left/Mild", 
                                  scale = (WIDTH,HEIGHT)),
                2: import_folder( path = "../Graphics/Weather/Rain/left/Heavy",
                                 scale = (WIDTH,HEIGHT))
            },
            'rain_right': {
                1: import_folder( path = "../Graphics/Weather/Rain/right/Mild", 
                                  scale = (WIDTH,HEIGHT)),
                2: import_folder( path = "../Graphics/Weather/Rain/right/Heavy",
                                 scale = (WIDTH,HEIGHT))
            },
            'snow_right': {
                1: import_folder(path = "../Graphics/Weather/Snow/right/Mild",
                                 scale = (WIDTH,HEIGHT)),
                2: import_folder(path = "../Graphics/Weather/Snow/right/Heavy",
                                 scale = (WIDTH,HEIGHT))
            },
            
            'snow_left': {
                1: import_folder(path = "../Graphics/Weather/Snow/left/Mild",
                                 scale = (WIDTH,HEIGHT)),
                2: import_folder(path = "../Graphics/Weather/Snow/left/Heavy",
                                 scale = (WIDTH,HEIGHT))
            }
        }
        self.active = False
        self.alpha = 40  # Adjust the alpha value as needed
      
        # Apply transparency to all frames of the animations upon initialization
        for weather_type in self.weather_animations:
            for intensity in self.weather_animations[weather_type]:
                for frame_index in range(len(self.weather_animations[weather_type][intensity])):
                    frame = self.weather_animations[weather_type][intensity][frame_index]
                    self.weather_animations[weather_type][intensity][frame_index] = self.make_transparent(frame, self.alpha)
    
    
    def make_transparent(self, image, alpha):
        # Create a transparent version of the image with the specified alpha value
        transparent_image = image.copy()
        transparent_image.set_alpha(alpha)
        return transparent_image

    def set_weather(self, weather_type, intensity, wind_direction):
        weather_type_pre = self.weather_type 
        if weather_type == 'clear':
            self.active = False
            self.weather_type = weather_type
            if weather_type_pre != weather_type:
                self.current_animation = []
                self.current_frame_index = 0
        else:
            if weather_type_pre != weather_type:
                # Determine whether wind is blowing left or right
                wind_direction_str = 'left' if wind_direction <= 180 else 'right'
                # Select the appropriate animation based on weather type and wind direction
                animation_key = f"{weather_type}_{wind_direction_str}"
                self.current_animation = self.weather_animations[animation_key][intensity]
                self.active = True
                self.weather_type = weather_type
                self.current_frame_index = 0  # Reset to the start of the animation
                self.last_frame_update_time = pygame.time.get_ticks()  # Reset the animation timer

    def update(self, dt):
        #print(f"update weather: {self.active} {self.current_frame_index}")
        if self.active and self.current_animation:
            current_time = pygame.time.get_ticks()
            #print(f"current time {current_time} {self.last_frame_update_time}")
            #print(f"{current_time - self.last_frame_update_time}")
            if current_time - self.last_frame_update_time > self.frame_duration:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.current_animation)
                self.last_frame_update_time = current_time

    def draw(self):
        if self.active:
            # Render the current frame of the animation
            frame = self.current_animation[self.current_frame_index]
            self.display_surface.blit(frame, (0, 0))
