import pygame

from entities.towers.basic_tower import BasicTower
from utils.settings import BACKGROUND_COLOR


def create_render_layers(screen_size):
    return {
        "grid": pygame.Surface(screen_size, pygame.SRCALPHA),
        "ui": pygame.Surface(screen_size, pygame.SRCALPHA),
        "tower": pygame.Surface(screen_size, pygame.SRCALPHA),
        "projectile": pygame.Surface(screen_size, pygame.SRCALPHA),
        "enemy": pygame.Surface(screen_size, pygame.SRCALPHA)
    }


def draw_game(
    screen,
    layers,
    game_state,
    menu,
    radial_menu,
    main_menu,
    data_log,
    victory_screen,
    game_over_screen
):
    screen.fill(BACKGROUND_COLOR)
    _clear_layers(layers)

    game_state.grid.draw(
        layers["grid"],
        layers["grid"].get_width(),
        layers["grid"].get_height()
    )

    game_state.enemies.draw(layers["enemy"])
    game_state.towers.draw(layers["tower"])
    game_state.projectiles.draw(layers["projectile"])

    menu.draw(
        layers["ui"],
        game_state.wave_manager.current_wave_number,
        game_state.enemies_killed,
        game_state.metal,
        BasicTower.cost,
        game_state.player_health,
        game_state.wave_manager.cleared_wave,
        game_state.wave_manager.all_waves_complete
    )

    radial_menu.draw(layers["ui"], pygame.mouse.get_pos())
    main_menu.draw_button(layers["ui"])
    data_log.draw(layers["ui"])
    main_menu.draw_overlay(layers["ui"])

    if game_state.victory_open:
        victory_screen.draw(layers["ui"])

    if game_state.game_over_started_at is not None:
        game_over_screen.draw(layers["ui"])

    _blit_layers(screen, layers)


def _clear_layers(layers):
    for layer in layers.values():
        layer.fill((0, 0, 0, 0))


def _blit_layers(screen, layers):
    for layer_name in ("grid", "tower", "projectile", "enemy", "ui"):
        screen.blit(layers[layer_name], (0, 0))
