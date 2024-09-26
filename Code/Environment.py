import random
import pygame

class Weather:
    def __init__(self):
        self.current_time = 0  # Track time in hours
        self.day_length = 24  # Length of a day in hours
        self.wind_direction = 0  # Degrees, where 0 degrees is north
        self.wind_intensity = 0  # Arbitrary units
        self.temperature = 20  # Celsius
        self.light_level = 1  # Default to full daylight

    def update_weather(self, dt):
        # Update the current time within the day
        self.current_time = (self.current_time + dt) % self.day_length
        # Update wind, temperature, and light level based on the new time
        self.randomize_wind()
        self.update_temperature()
        self.update_light_level()

    def randomize_wind(self):
        # Adjust wind direction randomly within a 20-degree range
        self.wind_direction = (self.wind_direction + random.uniform(-10, 10)) % 360
        # Adjust wind intensity, ensuring it stays non-negative
        self.wind_intensity = max(0, self.wind_intensity + random.uniform(-0.5, 0.5))

    def update_temperature(self):
        # Simulate a simple diurnal cycle of temperature
        if 6 <= self.current_time < 18:  # Daytime temperatures rise
            self.temperature = max(10, min(30, self.temperature + 0.1))
        else:  # Nighttime temperatures fall
            self.temperature = max(10, min(30, self.temperature - 0.1))

    def update_light_level(self):
        # Calculate light level based on the time of day, includes smooth transitions
        if 6 <= self.current_time < 18:
            self.light_level = 1  # Full daylight
        elif 18 <= self.current_time < 20:
            self.light_level = 0.5 + 0.5 * (20 - self.current_time) / 2  # Dusk
        elif 4 <= self.current_time < 6:
            self.light_level = 0.5 + 0.5 * (self.current_time - 4) / 2  # Dawn
        else:
            self.light_level = 0.5  # Night
