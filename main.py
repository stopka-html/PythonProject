import pygame
from types import SimpleNamespace

from utils.settings import  *

from systems.wave_parameters import WAVES
from systems.game_reset import GameReset
from systems.ui.main_menu import MainMenu
from systems.ui.radial_menu import RadialMenu
from systems.ui.radial_menu_enemy import create_enemy_options
from systems.ui.radial_menu_tower import (
    create_build_options
)
from systems.ui.menu import Menu
from systems.ui.data_log import DataLog
from systems.ui.victory_screen import VictoryScreen
from systems.ui.game_over_screen import GameOverScreen
from systems.game_input import GameInputHandler
from systems.game_renderer import create_render_layers, draw_game
from systems import audio
#This main function is actually incomprehensible 
# TODO:
# Add a high-tier boss enemy.
# Finish turret and enemy balancing.
pygame.init()
pygame.display.set_caption("Iron Dome")
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

clock = pygame.time.Clock()

runtime_settings = {
    "FPS": FPS,
    "GRID_SIZE": GRID_SIZE,
    "STARTING_METAL": STARTING_METAL,
    "STARTING_HEALTH": STARTING_HEALTH,
    "EFFECTS_VOLUME": EFFECTS_VOLUME,
    "MUSIC_VOLUME": MUSIC_VOLUME
}
game_reset = GameReset(SCREEN_WIDTH, SCREEN_HEIGHT, WAVES)


def apply_audio_settings():
    audio.configure(
        runtime_settings["EFFECTS_VOLUME"],
        runtime_settings["MUSIC_VOLUME"]
    )


apply_audio_settings()


def unpack_state(state):
    return (
        state["path_tiles"],
        state["grid"],
        state["path"],
        state["wave_manager"],
        state["enemies"],
        state["towers"],
        state["projectiles"],
        state["metal"],
        state["player_health"],
        state["enemies_killed"]
    )


game_state = game_reset.create_state(
    runtime_settings["STARTING_METAL"],
    runtime_settings["STARTING_HEALTH"],
    runtime_settings["GRID_SIZE"]
)
game_context = SimpleNamespace(
    **dict(zip(
        (
            "path_tiles",
            "grid",
            "path",
            "wave_manager",
            "enemies",
            "towers",
            "projectiles",
            "metal",
            "player_health",
            "enemies_killed"
        ),
        unpack_state(game_state)
    )),
    game_over_started_at=None,
    victory_open=False
)


def reset_progress():
    state = game_reset.create_state(
        runtime_settings["STARTING_METAL"],
        runtime_settings["STARTING_HEALTH"],
        runtime_settings["GRID_SIZE"]
    )
    return (*unpack_state(state), None)


menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
data_log = DataLog(SCREEN_WIDTH, SCREEN_HEIGHT)
victory_screen = VictoryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
game_over_screen = GameOverScreen()
main_menu = MainMenu(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    runtime_settings
)

render_layers = create_render_layers((SCREEN_WIDTH, SCREEN_HEIGHT))
radial_menu = RadialMenu()
build_options = create_build_options()
enemy_options = create_enemy_options()
input_handler = GameInputHandler(
    screen,
    menu,
    main_menu,
    data_log,
    radial_menu,
    victory_screen,
    build_options,
    enemy_options,
    reset_progress,
    apply_audio_settings
)

running = True
#Main game loop
while running:

    clock.tick(runtime_settings["FPS"])
    audio.update_music()

    for event in pygame.event.get():
        if not input_handler.handle_event(event, game_context):
            running = False

    if (
        game_context.game_over_started_at is None
        and not main_menu.is_open
        and not data_log.is_open
        and not game_context.victory_open
    ):
        wave_was_active = game_context.wave_manager.wave_active
        game_context.wave_manager.update(game_context.enemies, game_context.path)

        
        game_context.enemies.update()

        
        game_context.towers.update(game_context.enemies, game_context.projectiles)

        game_context.projectiles.update()

        for enemy in list(game_context.enemies):
            if enemy.reached_end and not enemy.metal_collected:
                game_context.player_health -= enemy.metal_reward
                enemy.metal_collected = True
            elif not enemy.alive and not enemy.metal_collected:
                game_context.metal += enemy.metal_reward
                game_context.enemies_killed += 1
                enemy.metal_collected = True
                audio.play_random_explosion()
            if not enemy.alive:
                game_context.enemies.remove(enemy)
        game_context.wave_manager.check_cleared_wave(game_context.enemies)
        if wave_was_active and not game_context.wave_manager.wave_active:
            audio.play_sfx("wave_over")

        if game_context.wave_manager.all_waves_complete:
            game_context.victory_open = True
            radial_menu.close()
            main_menu.close()

        for project in list(game_context.projectiles):
            if not project.active:
                game_context.projectiles.remove(project)

        if game_context.player_health <= 0:
            game_context.player_health = 0
            game_context.game_over_started_at = pygame.time.get_ticks()
            audio.play_sfx("game_over")
            radial_menu.close()
            main_menu.close()

    if game_context.game_over_started_at is not None:
        elapsed_time = pygame.time.get_ticks() - game_context.game_over_started_at

        if elapsed_time >= 3000:
            (
                game_context.path_tiles,
                game_context.grid,
                game_context.path,
                game_context.wave_manager,
                game_context.enemies,
                game_context.towers,
                game_context.projectiles,
                game_context.metal,
                game_context.player_health,
                game_context.enemies_killed,
                game_context.game_over_started_at
            ) = reset_progress()
            data_log._is_open = False
            data_log._is_dissmissed = False
            game_context.victory_open = False

    draw_game(
        screen,
        render_layers,
        game_context,
        menu,
        radial_menu,
        main_menu,
        data_log,
        victory_screen,
        game_over_screen
    )

    pygame.display.flip()

pygame.quit()
