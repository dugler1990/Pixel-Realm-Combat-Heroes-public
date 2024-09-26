import cProfile
import pstats
import pygame
import sys
import os
import psutil

from Main2 import Game

def profile_game():
    game = Game()
    game.run()

if __name__ == "__main__":
    # Run the game with profiling
    cProfile.run('profile_game()', 'game_profile.prof')

    # Print profiling results
    profiler_stats = pstats.Stats('game_profile.prof')
    profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(20)
