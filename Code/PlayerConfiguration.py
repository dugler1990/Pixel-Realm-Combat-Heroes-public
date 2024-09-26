import pygame

class PlayerConfiguration:
    def __init__(self,
                 input_manager,
                 base_stats,
                 remaining_points,
                 game = None):

        self.input_manager = input_manager
        if game : 
            self.screen = game.screen
        self.base_stats = base_stats
        self.final_stats = base_stats.copy()
        self.remaining_points = remaining_points
        self.font = pygame.font.Font(None, 30)
        self.selected_stat_index = 0
        self.create_plus_buttons()
        self.stats_list = list(self.plus_buttons.keys())
        self.update_game_variables()
        self.update_stickman()
        self.finished = False

    def create_plus_buttons(self):
        self.plus_buttons = {
            "magic":pygame.Rect(300, 100, 20, 20),
            "strength": pygame.Rect(300, 150, 20, 20),
            "vitality": pygame.Rect(300, 200, 20, 20),
            "agility": pygame.Rect(300, 250, 20, 20),
            "charisma": pygame.Rect(300, 300, 20, 20),
            "ready": pygame.Rect(500, 400, 100, 60)
        }


    def add_remaining_points(self, n):
        self.remaining_points += n 

    def handle_events(self, level=None):
        #print(self.selected_stat_index)
        if self.input_manager.is_key_just_pressed(pygame.K_DOWN):
            self.selected_stat_index = (self.selected_stat_index + 1) % len(self.stats_list)
        elif self.input_manager.is_key_just_pressed(pygame.K_UP):
            self.selected_stat_index = (self.selected_stat_index - 1) % len(self.stats_list)
            
        elif self.input_manager.is_key_just_pressed(pygame.K_RETURN) and self.remaining_points > 0 and self.selected_stat_index != 5:
            selected_stat = self.stats_list[self.selected_stat_index]
            self.final_stats[selected_stat] += 1
            self.remaining_points -= 1
            self.update_game_variables()
            self.update_stickman()
            
        elif self.input_manager.is_key_just_pressed(pygame.K_RETURN) and self.remaining_points == 0 and self.selected_stat_index == 5:
            if level:
                level.toggle_player_config()
                level.update_player_stats()
            self.finished = True
        elif self.input_manager.is_key_just_pressed(pygame.K_BACKSPACE) :
            selected_stat = self.stats_list[self.selected_stat_index]
            #print("selected_stat")
            #print(selected_stat)
            #print(self.final_stats[selected_stat] )
            #print(self.base_stats[selected_stat])
            
            # Check if the current value is strictly greater than the base stat
            if self.final_stats[selected_stat] > self.base_stats[selected_stat]:
                self.final_stats[selected_stat] -= 1
                self.remaining_points += 1
                self.update_game_variables()
                self.update_stickman()
            

    def update_stickman(self):
        # Update the stickman based on the stats
        self.stickman_thickness = 2 + self.final_stats["strength"] // 5
        self.head_radius = 20 + self.final_stats["magic"] // 2
        self.body_length = 50 + self.final_stats["strength"] // 2
        self.leg_length = 40 + self.final_stats["agility"] * 2
        self.heart_size = 5 + self.final_stats["vitality"] // 2 

    def update_game_variables(self):
        self.final_stats["attack"] = self.base_stats["attack"] + self.final_stats["strength"] * 2
        self.final_stats["energy"] = self.base_stats["magic"] + self.final_stats["magic"] * 50
        self.final_stats["health"] = self.base_stats["vitality"] + self.final_stats["vitality"] * 50
        self.final_stats["speed"] = self.base_stats["speed"] + self.final_stats["agility"] * 0.2
        

    def draw(self, screen = None, new_points = None):

        if screen :
            self.screen = screen
        self.screen.fill((0, 0, 0))  # Clear screen
        y_offset = 100
        for stat, value in self.final_stats.items():
            
            
            # WL see here , im working with an attribute called mana that doesnt actually exist.
            
            
            if stat not in ["attack", "energy", "speed","health"]:  # Avoid displaying these derived stats here
                
                text = self.font.render(f"{stat.capitalize()}: {value}", True, pygame.Color('white'))
                self.screen.blit(text, (100, y_offset))
                box_rect = self.plus_buttons.get(stat, pygame.Rect(0, 0, 0, 0))
                pygame.draw.rect(self.screen, pygame.Color('red'), box_rect)

                if self.stats_list[self.selected_stat_index] == stat:
                    pygame.draw.rect(self.screen, pygame.Color('white'), box_rect, 2)  # White outline for selected box

                y_offset += 50

        text = self.font.render(f"Remaining Points: {self.remaining_points}", True, pygame.Color('white'))
        self.screen.blit(text, (100, 50))

        # Display derived stats
        derived_y_offset = 350
        derived_stats_texts = [
            f"Health: {self.final_stats['health']}",
            f"Attack: {self.final_stats['attack']}",
            f"Energy: {self.final_stats['energy']}",
            f"Speed: {self.final_stats['speed']}"
        ]
        for stat_text in derived_stats_texts:
            text = self.font.render(stat_text, True, pygame.Color('white'))
            self.screen.blit(text, (100, derived_y_offset))
            derived_y_offset += 30

        # Draw ready button
        box_rect = self.plus_buttons['ready'] # TODO: These are actually all buttons needs refactor 
        pygame.draw.rect( self.screen, pygame.Color("red"), box_rect )
        
        #print("checking len for white outline")
        #print(self.selected_stat_index )
        #print(len(self.stats_list))
        
        if self.selected_stat_index == len(self.stats_list)-1:
            #print("drawing white outline on box")
            pygame.draw.rect(self.screen, pygame.Color('white'), box_rect, 2)  # White outline for selected box

        
        font = pygame.font.Font(None, 24)          
        text_surface = font.render("READY !!!", True, pygame.Color('white'))
        text_rect = text_surface.get_rect()
        text_rect.center = box_rect.center
        
        self.screen.blit(text_surface, text_rect)

        # Draw stickman based on actual stats
        self.draw_stickman()

        pygame.display.update()

    def draw_stickman(self):
        center_x, center_y = 550, 200

        # Draw head
        pygame.draw.circle(self.screen, pygame.Color('white'), (center_x, center_y - self.body_length), self.head_radius, self.stickman_thickness)

        # Draw body
        pygame.draw.line(self.screen, pygame.Color('white'), (center_x, center_y - self.body_length), (center_x, center_y), self.stickman_thickness)

        # Draw arms
        pygame.draw.line(self.screen, pygame.Color('white'), (center_x, center_y - self.body_length // 2), (center_x - 40, center_y - self.body_length // 2), self.stickman_thickness)
        pygame.draw.line(self.screen, pygame.Color('white'), (center_x, center_y - self.body_length // 2), (center_x + 40, center_y - self.body_length // 2), self.stickman_thickness)

        # Draw legs
        pygame.draw.line(self.screen, pygame.Color('white'), (center_x, center_y), (center_x - self.leg_length, center_y + self.leg_length), self.stickman_thickness)
        pygame.draw.line(self.screen, pygame.Color('white'), (center_x, center_y), (center_x + self.leg_length, center_y + self.leg_length), self.stickman_thickness)

        # Draw heart
        
        heart_points = [
            (center_x, center_y - self.body_length // 2 - self.heart_size // 2),
            (center_x - self.heart_size // 2, center_y - self.body_length // 2),
            (center_x, center_y - self.body_length // 2 + self.heart_size // 2),
            (center_x + self.heart_size // 2, center_y - self.body_length // 2)
        ]

        pygame.draw.polygon(self.screen, pygame.Color('red'), heart_points)