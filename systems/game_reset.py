from game.grid import Grid
from game.path import create_default_path
from game.wave import WaveManager
import pygame


class GameReset:

    def __init__(self, width, height, waves):
        self.width = width
        self.height = height
        self.waves = waves

    def create_state(self, starting_metal, starting_health, grid_size):
        path_tiles = create_default_path(
            self.width,
            self.height,
            grid_size
        )
        grid = Grid(
            self.width,
            self.height,
            path_tiles,
            grid_size
        )

        return {
            "path_tiles": path_tiles,
            "grid": grid,
            "path": grid.get_path_points(),
            "wave_manager": WaveManager(self.waves),
            "enemies": pygame.sprite.Group(),
            "towers": pygame.sprite.Group(),
            "projectiles": pygame.sprite.Group(),
            "metal": starting_metal,
            "player_health": starting_health,
            "enemies_killed": 0
        }
