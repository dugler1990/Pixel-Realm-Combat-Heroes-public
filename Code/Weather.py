import random
import pygame
import math

class Weather:
    def __init__(self):
        self.current_time = random.randint(0,24)  # Track time in hours
        self.day_length = 24  # Length of a day in hours
        self.wind_direction = 0  # Degrees, where 0 degrees is north
        self.wind_intensity = 0  # Arbitrary units
        self.temperature = 20  # Celsius
        self.light_level = 1  # Default to full daylight
        self.weather_type = 'snow'
        self.weather_intensity = 2
        
    def update(self, dt):
        # Update the current time within the day
        #print(f"dt : {dt}")
        time_increment = dt 
        #print(time_increment)
        # Update the current time within the day
        self.current_time = (self.current_time + time_increment*10) % self.day_length

        # Update wind, temperature, and light level based on the new time
        self.randomize_wind()
        self.update_precipitation()
        self.update_temperature()
        self.update_light_level()

    def calculate_wind_force(self):
        # Convert wind direction from degrees to radians
        wind_direction_rad = math.radians(self.wind_direction)

        # Calculate horizontal and vertical components
        horizontal_force = self.wind_intensity * math.cos(wind_direction_rad)
        vertical_force = self.wind_intensity * math.sin(wind_direction_rad)

        return horizontal_force, vertical_force



    def randomize_wind(self):
        #print(f"wind force: {self.wind_intensity}")
        #print(f"wind direction: {self.wind_direction}")
        #print(f"current time : {self.current_time}")
        # Adjust wind direction randomly within a 20-degree range
        self.wind_direction = (self.wind_direction + random.uniform(-10, 10)) % 360
        # Adjust wind intensity, ensuring it stays non-negative
        self.wind_intensity = max(0, self.wind_intensity + random.uniform(-0.52, 0.5))

    def update_temperature(self):
        
        # Check if it's the start of a new day
        if self.current_time > 0 and self.current_time < 0.0001:
            # Randomize temperature at the start of each day
            self.temperature = random.uniform(-15, 10)
        
        # Simulate a simple diurnal cycle of temperature
        #print(f" temp : {self.temperature}")
        if 6 <= self.current_time < 18:  # Daytime temperatures rise
            self.temperature = max(-20, min(30, self.temperature + random.gauss(0.5, 2)))
        else:  # Nighttime temperatures fall
            self.temperature = max(-20, min(30, self.temperature - random.gauss(0.5, 2)))
            
    def update_precipitation(self):
        #print(f" prec : {self.weather_type} ")
        
        if (self.temperature < 0) and (self.weather_type == 'rain'): self.weather_type = 'snow'
        if (self.temperature > 0) and (self.weather_type == 'snow'): self.weather_type = 'rain'
        
        if random.randint(0,1000) == 1000: 
            #print('meant to change precipitation')
            if self.weather_type == 'clear':
                self.weather_type ='rain'
            if self.weather_type in ['rain','snow']:
                self.weather_type == 'clear'
            

    def update_light_level(self):
        # Calculate light level based on the time of day, includes smooth transitions
        if 60 <= self.current_time < 180:
            self.light_level = 1  # Full daylight
        elif 180 <= self.current_time < 200:
            self.light_level = 0.5 + 0.5 * (200 - self.current_time) / 2  # Dusk
        elif 4 <= self.current_time < 6:
            self.light_level = 0.5 + 0.5 * (self.current_time - 40) / 2  # Dawn
        else:
            self.light_level = 0.5  # Night
