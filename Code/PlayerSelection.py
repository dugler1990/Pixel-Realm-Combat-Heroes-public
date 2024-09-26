import pygame
import json
with open("../Graphics/PlayerSelectionDict.json","r") as file:
    player_dir_dict =  json.loads( file.read() )
print(player_dir_dict)

unlocked_player_positions = [(x['selection_position']["x"],x["selection_position"]["y"]) for x in player_dir_dict["Players"]]
unlocked_player_directory = [x['player_info_dir'] for x in player_dir_dict["Players"]]
unlocked_player_base_stats = [x['base_stats'] for x in player_dir_dict["Players"]]

print(unlocked_player_positions)

class PlayerSelection:
    def __init__(self, game, input_manager):
        self.game = game
        self.input_manager = input_manager
        self.screen = game.screen
        self.grid_columns = 4
        self.grid_rows = 3
        self.grid_size = self.screen.get_width() // self.grid_columns, self.screen.get_height() // self.grid_rows
        self.selected_option = (0, 0)  # (row, column)
        self.default_player_image = pygame.image.load("../Graphics/Orange_Wizard/down_idle/0.png").convert()
        self.selected_player_info_dir = None
    def draw_grid(self):
        for row in range(self.grid_rows):
            for col in range(self.grid_columns):
                rect = pygame.Rect(col * self.grid_size[0], row * self.grid_size[1], self.grid_size[0], self.grid_size[1])
                if (row, col) == self.selected_option:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                if (row,col) in unlocked_player_positions :  # Example to draw the default player image in the first cell
                    index = unlocked_player_positions.index((row,col))
                    image_dir = unlocked_player_directory[index]
                    player_image = pygame.image.load(image_dir+"/selection_screen/0.png").convert()
                    self.screen.blit(pygame.transform.scale(player_image, self.grid_size), (rect.x, rect.y))

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.draw_grid()
        pygame.display.flip()

    def handle_events(self):
        row, col = self.selected_option
        if self.input_manager.is_key_just_pressed(pygame.K_UP) and row > 0:
            self.selected_option = (row - 1, col)
        elif self.input_manager.is_key_just_pressed(pygame.K_DOWN) and row < self.grid_rows - 1:
            self.selected_option = (row + 1, col)
        elif self.input_manager.is_key_just_pressed(pygame.K_LEFT) and col > 0:
            self.selected_option = (row, col - 1)
        elif self.input_manager.is_key_just_pressed(pygame.K_RIGHT) and col < self.grid_columns - 1:
            self.selected_option = (row, col + 1)
        elif self.input_manager.is_key_just_pressed(pygame.K_RETURN):
            self.select_player(row,col)

    def select_player(self,row,col):
        # Here you can define the logic for what happens when a player is selected
        # For now, it will just print the selected grid position
        print(f"Selected Player at Grid: {self.selected_option}")
        # Example to start the game with the selected player
        # You will need to modify this to actually start the game with the selected player
        self.selected_player_info_dir = unlocked_player_directory[ unlocked_player_positions.index((row,col))]
        self.game.in_player_selection = False  # Assuming you have a flag in your game class to manage this
        self.base_stats = unlocked_player_base_stats[ unlocked_player_positions.index((row,col)) ]
         
