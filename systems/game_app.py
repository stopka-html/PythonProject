import pygame

from systems import audio
from systems.game_input import GameInputHandler
from systems.game_renderer import create_render_layers, draw_game
from systems.game_session import GameSession
from systems.ui.data_log import DataLog
from systems.ui.game_over_screen import GameOverScreen
from systems.ui.main_menu import MainMenu
from systems.ui.menu import Menu
from systems.ui.radial_menu import RadialMenu
from systems.ui.radial_menu_enemy import create_enemy_options
from systems.ui.radial_menu_tower import create_build_options
from systems.ui.victory_screen import VictoryScreen
from systems.wave_parameters import WAVES
from utils.settings import (
    EFFECTS_VOLUME,
    FPS,
    GRID_SIZE,
    MUSIC_VOLUME,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STARTING_HEALTH,
    STARTING_METAL
)


class GameApp:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Iron Dome")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.settings = self._create_runtime_settings()
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.data_log = DataLog(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.victory_screen = VictoryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_over_screen = GameOverScreen()
        self.main_menu = MainMenu(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.settings
        )
        self.radial_menu = RadialMenu()
        self.session = GameSession(
            self.settings,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            WAVES,
            self.radial_menu,
            self.main_menu,
            self.data_log
        )
        self.render_layers = create_render_layers((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.input_handler = self._create_input_handler()
        self.running = True
        self.apply_audio_settings()

    def run(self):
        try:
            while self.running:
                self._tick()
        finally:
            pygame.quit()

    def apply_audio_settings(self):
        audio.configure(
            self.settings["EFFECTS_VOLUME"],
            self.settings["MUSIC_VOLUME"]
        )

    def _tick(self):
        self.clock.tick(self.settings["FPS"])
        audio.update_music()
        self._handle_events()
        self.session.update()
        self._draw()
        pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if not self.input_handler.handle_event(event, self.session.state):
                self.running = False

    def _draw(self):
        draw_game(
            self.screen,
            self.render_layers,
            self.session.state,
            self.menu,
            self.radial_menu,
            self.main_menu,
            self.data_log,
            self.victory_screen,
            self.game_over_screen
        )

    def _create_input_handler(self):
        return GameInputHandler(
            self.screen,
            self.menu,
            self.main_menu,
            self.data_log,
            self.radial_menu,
            self.victory_screen,
            create_build_options(),
            create_enemy_options(),
            self.session.reset_progress,
            self.apply_audio_settings
        )

    def _create_runtime_settings(self):
        return {
            "FPS": FPS,
            "GRID_SIZE": GRID_SIZE,
            "STARTING_METAL": STARTING_METAL,
            "STARTING_HEALTH": STARTING_HEALTH,
            "EFFECTS_VOLUME": EFFECTS_VOLUME,
            "MUSIC_VOLUME": MUSIC_VOLUME
        }
