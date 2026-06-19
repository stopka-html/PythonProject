import pygame

from utils.settings import *

from entities.towers.basic_tower import BasicTower
from systems.wave_parameters import WAVES
from systems.game_reset import GameReset
from systems.main_menu import MainMenu
from systems.radial_menu import RadialMenu
from systems.radial_menu_enemy import create_enemy_options
from systems.radial_menu_tower import (
    create_affordable_build_options,
    create_build_options
)
from systems.menu import Menu
from systems.data_log import DataLog
from systems.victory_screen import VictoryScreen
from systems import audio

# TODO:
# Add a high-tier boss enemy.
# Add more waves.
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
(
    path_tiles,
    grid,
    path,
    wave_manager,
    enemies,
    towers,
    projectiles,
    metal,
    player_health,
    enemies_killed
) = unpack_state(game_state)

game_over_started_at = None

# TODO: Move the ui drawing out of main.py, into its own separate class.
def reset_progress():
    state = game_reset.create_state(
        runtime_settings["STARTING_METAL"],
        runtime_settings["STARTING_HEALTH"],
        runtime_settings["GRID_SIZE"]
    )
    return (*unpack_state(state), None)


def draw_game_over(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 30)

    title = title_font.render("Game Over", True, (255, 90, 90))
    title_rect = title.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 28)
    )
    screen.blit(title, title_rect)

    subtitle = small_font.render(
        "Resetting progress...",
        True,
        (235, 235, 245)
    )
    subtitle_rect = subtitle.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 32)
    )
    screen.blit(subtitle, subtitle_rect)


#This main function is actually incomprehensible 
menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
data_log = DataLog(SCREEN_WIDTH, SCREEN_HEIGHT)
victory_screen = VictoryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
main_menu = MainMenu(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    runtime_settings
)
radial_menu = RadialMenu()
build_options = create_build_options()
enemy_options = create_enemy_options()
data_log_open = False
data_log_dismissed = False
victory_open = False

running = True
#Main game loop
while running:

    clock.tick(runtime_settings["FPS"])
    audio.update_music()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            action = main_menu.handle_mouse_motion(event.pos)
            if action == "settings_changed":
                apply_audio_settings()

        if event.type == pygame.MOUSEBUTTONUP:
            main_menu.handle_mouse_up()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_over_started_at is not None:
                    continue

                if victory_open:
                    continue
                elif data_log_open:
                    data_log_open = False
                    data_log_dismissed = True
                elif radial_menu.is_open:
                    radial_menu.close()
                else:
                    main_menu.toggle()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over_started_at is not None:
                continue

            mouse_pos = event.pos
            gx, gy = grid.world_to_grid(mouse_pos)

            if victory_open:
                if victory_screen.restart_contains(mouse_pos):
                    (
                        path_tiles,
                        grid,
                        path,
                        wave_manager,
                        enemies,
                        towers,
                        projectiles,
                        metal,
                        player_health,
                        enemies_killed,
                        game_over_started_at
                    ) = reset_progress()
                    data_log_open = False
                    data_log_dismissed = False
                    victory_open = False
                continue

            if data_log_open:
                if data_log.close_contains(mouse_pos):
                    data_log_open = False
                    data_log_dismissed = True
                continue

            if (
                not data_log_dismissed
                and data_log.button_contains(mouse_pos)
            ):
                data_log_open = True
                radial_menu.close()
                main_menu.close()
                continue

            if (
                main_menu.main_button_contains(mouse_pos)
                or main_menu.is_open
            ):
                radial_menu.close()
                action = main_menu.handle_click(mouse_pos)

                if action == "settings_changed":
                    apply_audio_settings()

                if action == "restart":
                    (
                        path_tiles,
                        grid,
                        path,
                        wave_manager,
                        enemies,
                        towers,
                        projectiles,
                        metal,
                        player_health,
                        enemies_killed,
                        game_over_started_at
                    ) = reset_progress()
                    data_log_open = False
                    data_log_dismissed = False
                    victory_open = False

                continue

            if menu.wave_button_clicked(
                mouse_pos,
                wave_manager.cleared_wave
            ):
                radial_menu.close()
                if wave_manager.start_next_wave():
                    audio.play_sfx("wave_start")
                    audio.start_music()
                continue

            if menu.wave_button_contains(mouse_pos):
                radial_menu.close()
                continue

            selected_option = radial_menu.get_selected_option(mouse_pos)

            if selected_option and selected_option.payload:
                tower_class = selected_option.payload
                if metal >= tower_class.cost:
                    wx, wy = radial_menu.world_pos
                    towers.add(
                        tower_class(wx, wy)
                    )
                    metal -= tower_class.cost
                    grid.place(*radial_menu.grid_pos)
                    radial_menu.close()
                continue

            if radial_menu.grid_pos == (gx, gy):
                radial_menu.close()
                continue

            if radial_menu.contains(mouse_pos):
                continue

            wx, wy = grid.grid_to_world(
                gx,
                gy,
                clamp=True
            )

            if (gx, gy) in grid.path_tiles:
                radial_menu.open(
                    (gx, gy),
                    (wx, wy),
                    screen.get_size(),
                    enemy_options
                )
            elif grid.can_place(gx, gy):
                affordable_build_options = create_affordable_build_options(
                    build_options,
                    metal
                )

                radial_menu.open(
                    (gx, gy),
                    (wx, wy),
                    screen.get_size(),
                    affordable_build_options
                )
            else:
                radial_menu.close()

    if (
        game_over_started_at is None
        and not main_menu.is_open
        and not data_log_open
        and not victory_open
    ):
        wave_was_active = wave_manager.wave_active
        wave_manager.update(enemies, path)

        
        enemies.update()

        
        towers.update(enemies, projectiles)

        projectiles.update()

        for enemy in list(enemies):
            if enemy.reached_end and not enemy.metal_collected:
                player_health -= enemy.metal_reward
                enemy.metal_collected = True
            elif not enemy.alive and not enemy.metal_collected:
                metal += enemy.metal_reward
                enemies_killed += 1
                enemy.metal_collected = True
                audio.play_random_explosion()
            if not enemy.alive:
                enemies.remove(enemy)
        wave_manager.check_cleared_wave(enemies)
        if wave_was_active and not wave_manager.wave_active:
            audio.play_sfx("wave_over")

        if wave_manager.all_waves_complete:
            victory_open = True
            radial_menu.close()
            main_menu.close()

        for project in list(projectiles):
            if not project.active:
                projectiles.remove(project)

        if player_health <= 0:
            player_health = 0
            game_over_started_at = pygame.time.get_ticks()
            audio.play_sfx("game_over")
            radial_menu.close()
            main_menu.close()

    if game_over_started_at is not None:
        elapsed_time = pygame.time.get_ticks() - game_over_started_at

        if elapsed_time >= 3000:
            (
                path_tiles,
                grid,
                path,
                wave_manager,
                enemies,
                towers,
                projectiles,
                metal,
                player_health,
                enemies_killed,
                game_over_started_at
            ) = reset_progress()
            data_log_open = False
            data_log_dismissed = False
            victory_open = False

    screen.fill(BACKGROUND_COLOR)

    grid.draw(
        screen,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )

    
    enemies.draw(screen)

    towers.draw(screen)

    projectiles.draw(screen)

    menu.draw(
        screen,
        wave_manager.current_wave_number,
        enemies_killed,
        metal,
        BasicTower.cost,
        player_health,
        wave_manager.cleared_wave,
        wave_manager.all_waves_complete
    )

    radial_menu.draw(screen, pygame.mouse.get_pos())
    main_menu.draw_button(screen)
    if not data_log_dismissed and not data_log_open:
        data_log.draw_button(screen, pygame.time.get_ticks())
    main_menu.draw_overlay(screen)
    if data_log_open:
        data_log.draw_panel(screen)
    if victory_open:
        victory_screen.draw(screen)

    if game_over_started_at is not None:
        draw_game_over(screen)

    pygame.display.flip()

pygame.quit()
