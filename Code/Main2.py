import pygame, sys
from Settings import *
from Level4 import Level4
import os
from StartMenu import StartMenu
from PlayerSelection import PlayerSelection
from inputManager import InputManager
from LevelSelection import LevelSelection
from PlayerConfiguration import PlayerConfiguration
import psutil

level_8_layout_path = '../levels/Map8'
level_7_layout_path = '../levels/Map7'

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        # self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        # Set the fullscreen display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.clock = pygame.time.Clock()
        self.debug_info_surfaces = {} 


        self.input_manager = InputManager()
        self.level = None
        self.start_menu = StartMenu(self, self.input_manager)
        self.player_selection = PlayerSelection(self, self.input_manager)
        self.in_start_menu = True
        self.in_player_selection = False        
        self.state = "start_menu"  # Managing game states using a state variable
        main_sound = pygame.mixer.Sound("../Audio/Main.ogg")
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)
        self.level_selection = LevelSelection(self, self.input_manager)
        #self.player_configuration = PlayerConfiguration(self, self.input_manager)    
        self.in_level_selection = False  # New state for level selection
        self.show_debug_info = True 

        # Debug info update variables
        self.last_debug_update = 0
        self.debug_update_interval = 3000  # Update debug info every 500 milliseconds (0.5 seconds)

                # Initialize debug info variables
        self.debug_fps = 0
        self.debug_frame_time = 0
        self.debug_memory_usage = 0
        self.debug_cpu_usage = 0
        self.debug_sprite_count = 0
        self.debug_event_queue_length = 0        



    def start_level(self, level_number):
        player_info_dir = self.player_selection.selected_player_info_dir
        player_stats = self.player_configuration.final_stats 
        if player_info_dir is not None:
            if level_number == 7:
                self.level = Level4( self.input_manager, player_info_dir, level_7_layout_path, player_stats )
            elif level_number == 8:
                self.level = Level4( self.input_manager, player_info_dir, level_8_layout_path, player_stats )



            self.state = "level"  # Transition to the level


    #@profile
    def run(self):
        while True:
           # print(f" state in main : {self.state}")
            events = pygame.event.get()
            self.input_manager.update(events)

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == "start_menu":
                self.start_menu.handle_events()
                self.start_menu.draw()
                if not self.in_start_menu:
                    self.state = "player_selection"
                    self.in_player_selection = True
            elif self.state == "player_selection":
                self.player_selection.handle_events()
                self.player_selection.draw()
                if not self.in_player_selection:
                    self.state = "player_configuration"
                    
                    selected_player_base_stats = self.player_selection.base_stats
                    print("BASE STATS: ")
                    print(selected_player_base_stats)
                    self.player_configuration = PlayerConfiguration(input_manager =  self.input_manager,
                                                                    base_stats = selected_player_base_stats,
                                                                    remaining_points = 10,
                                                                    game = self)
            
            elif self.state == "player_configuration":
                self.player_configuration.handle_events()
                self.player_configuration.draw()
                print(f"in main finished indicattor: {self.player_configuration.finished }")
                if self.player_configuration.finished :  # Move to level selection when done
                    self.state = "level_selection"
                    self.in_level_selection = True
                    
            elif self.state == "level_selection":
                self.level_selection.handle_events()
                self.level_selection.draw()
                if not self.in_level_selection:  # If a level has been selected
                    # Assuming start_level method is defined to start the level
                    self.start_level(self.level_selection.selected_level)

            elif self.state == "level":### TODO: This is not actually used, the start:level method above is generally how it works, this is all still a bit messy
                self.level.run(dt)

            if self.show_debug_info:
                self.update_debug_info()
                self.display_debug_info()


            pygame.display.update()
            dt = self.clock.tick(FPS) /1000


    def update_debug_info(self):
        """Update the debug information."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_debug_update > self.debug_update_interval:
            self.last_debug_update = current_time

            # Update debug information
            self.debug_fps = self.clock.get_fps()
            self.debug_frame_time = self.clock.get_time()
            self.debug_memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            self.debug_cpu_usage = psutil.cpu_percent()
            if self.level:
                self.debug_sprite_count = len(self.level.layout_manager.visible_sprites)
            self.debug_event_queue_length = len(pygame.event.get())


    def display_debug_info(self):
        """Display the debug information on the screen, using cached text surfaces."""
        font = pygame.font.Font(None, 30)
        text_spacing = 30
        current_y = self.HEIGHT - 30

        # List of debug info keys and their corresponding values
        debug_info = [
            ("FPS", f"FPS: {int(self.debug_fps)}"),
            ("Frame Time", f"Frame Time: {self.debug_frame_time}ms"),
            ("Memory", f"Memory: {self.debug_memory_usage:.2f}MB"),
            ("CPU Usage", f"CPU Usage: {self.debug_cpu_usage}%"),
            ("Visible Sprites", f"Visible Sprites: {self.debug_sprite_count}"),
            ("Event Queue", f"Event Queue: {self.debug_event_queue_length}")
        ]

        for key, value in debug_info:
            # Check if the surface needs to be updated
            if key not in self.debug_info_surfaces or self.debug_info_surfaces[key]['value'] != value:
                # Render new text surface and cache it
                text_surface = font.render(value, True, pygame.Color('white'))
                self.debug_info_surfaces[key] = {'surface': text_surface, 'value': value}

            # Blit the cached text surface
            self.screen.blit(self.debug_info_surfaces[key]['surface'], (10, current_y))
            current_y -= text_spacing


if  __name__ == "__main__":
    game = Game()
    game.run()
