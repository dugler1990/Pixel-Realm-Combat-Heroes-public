import pygame
import sys

class StartMenu:
    def __init__(self, game, input_manager):
        self.game = game
        self.input_manager = input_manager
        self.screen = game.screen
        self.font = pygame.font.Font(None, 40)
        self.options = ["Start Game", "Settings"]
        self.selected_option = 0

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        for i, option in enumerate(self.options):
            color = (255, 0, 0) if i == self.selected_option else (255, 255, 255)
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2 + i * 50))
            self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def handle_events(self):
        if self.input_manager.is_key_just_pressed(pygame.K_UP):
            self.selected_option = max(0, self.selected_option - 1)
        elif self.input_manager.is_key_just_pressed(pygame.K_DOWN):
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif self.input_manager.is_key_just_pressed(pygame.K_RETURN):
            if self.selected_option == 0:  # Start Game Selected
                self.game.in_start_menu = False
            elif self.selected_option == 1:  # Settings Selected
                print("Settings selected")
