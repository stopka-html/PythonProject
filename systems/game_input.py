import pygame

from systems import audio
from systems.ui.radial_menu_tower import create_affordable_build_options


class GameInputHandler:

    def __init__(
        self,
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
    ):
        self.screen = screen
        self.menu = menu
        self.main_menu = main_menu
        self.data_log = data_log
        self.radial_menu = radial_menu
        self.victory_screen = victory_screen
        self.build_options = build_options
        self.enemy_options = enemy_options
        self.reset_progress = reset_progress
        self.apply_audio_settings = apply_audio_settings

    def handle_event(self, event, game_state):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)

        if event.type == pygame.MOUSEBUTTONUP:
            self.main_menu.handle_mouse_up()

        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event, game_state)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event, game_state)

        return True

    def _handle_mouse_motion(self, event):
        action = self.main_menu.handle_mouse_motion(event.pos)
        if action == "settings_changed":
            self.apply_audio_settings()

    def _handle_key_down(self, event, game_state):
        if event.key != pygame.K_ESCAPE:
            return

        if game_state.game_over_started_at is not None:
            return

        if game_state.victory_open:
            return

        if self.data_log.is_open:
            self.data_log._is_open = False
            self.data_log._is_dissmissed = True
        elif self.radial_menu.is_open:
            self.radial_menu.close()
        else:
            self.main_menu.toggle()

    def _handle_mouse_down(self, event, game_state):
        if game_state.game_over_started_at is not None:
            return

        mouse_pos = event.pos
        gx, gy = game_state.grid.world_to_grid(mouse_pos)

        if game_state.victory_open:
            self._handle_victory_click(mouse_pos, game_state)
            return

        if self.data_log.update(click=True, mouse_pos=mouse_pos):
            return

        if self._handle_main_menu_click(mouse_pos, game_state):
            return

        if self._handle_wave_button_click(mouse_pos, game_state):
            return

        self._handle_grid_click(mouse_pos, gx, gy, game_state)

    def _handle_victory_click(self, mouse_pos, game_state):
        if self.victory_screen.restart_contains(mouse_pos):
            self._restart(game_state)
            self.data_log._is_open = False
            self.data_log._is_dissmissed = False
            game_state.victory_open = False

    def _handle_main_menu_click(self, mouse_pos, game_state):
        if (
            not self.main_menu.main_button_contains(mouse_pos)
            and not self.main_menu.is_open
        ):
            return False

        self.radial_menu.close()
        action = self.main_menu.handle_click(mouse_pos)

        if action == "settings_changed":
            self.apply_audio_settings()

        if action == "restart":
            self._restart(game_state)
            self.data_log._is_dissmissed = False
            game_state.victory_open = False

        return True

    def _handle_wave_button_click(self, mouse_pos, game_state):
        if self.menu.wave_button_clicked(
            mouse_pos,
            game_state.wave_manager.cleared_wave
        ):
            self.radial_menu.close()
            if game_state.wave_manager.start_next_wave():
                audio.play_sfx("wave_start")
                audio.start_music()
            return True

        if self.menu.wave_button_contains(mouse_pos):
            self.radial_menu.close()
            return True

        return False

    def _handle_grid_click(self, mouse_pos, gx, gy, game_state):
        selected_option = self.radial_menu.get_selected_option(mouse_pos)

        if selected_option and selected_option.payload:
            self._try_build_selected_tower(selected_option, game_state)
            return

        if self.radial_menu.grid_pos == (gx, gy):
            self.radial_menu.close()
            return

        if self.radial_menu.contains(mouse_pos):
            return

        wx, wy = game_state.grid.grid_to_world(gx, gy, clamp=True)

        if (gx, gy) in game_state.grid.path_tiles:
            self.radial_menu.open(
                (gx, gy),
                (wx, wy),
                self.screen.get_size(),
                self.enemy_options
            )
        elif game_state.grid.can_place(gx, gy):
            affordable_build_options = create_affordable_build_options(
                self.build_options,
                game_state.metal
            )

            self.radial_menu.open(
                (gx, gy),
                (wx, wy),
                self.screen.get_size(),
                affordable_build_options
            )
        else:
            self.radial_menu.close()

    def _try_build_selected_tower(self, selected_option, game_state):
        tower_class = selected_option.payload
        if game_state.metal < tower_class.cost:
            return

        wx, wy = self.radial_menu.world_pos
        game_state.towers.add(tower_class(wx, wy))
        game_state.metal -= tower_class.cost
        game_state.grid.place(*self.radial_menu.grid_pos)
        self.radial_menu.close()

    def _restart(self, game_state):
        (
            game_state.path_tiles,
            game_state.grid,
            game_state.path,
            game_state.wave_manager,
            game_state.enemies,
            game_state.towers,
            game_state.projectiles,
            game_state.metal,
            game_state.player_health,
            game_state.enemies_killed,
            game_state.game_over_started_at
        ) = self.reset_progress()
