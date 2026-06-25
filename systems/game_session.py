import pygame

from systems import audio
from systems.game_state import GameStateFactory


GAME_OVER_RESET_DELAY_MS = 3000


class GameSession:

    def __init__(
        self,
        settings,
        screen_width,
        screen_height,
        waves,
        radial_menu,
        main_menu,
        data_log
    ):
        self.settings = settings
        self.radial_menu = radial_menu
        self.main_menu = main_menu
        self.data_log = data_log
        self.state_factory = GameStateFactory(screen_width, screen_height, waves)
        self.state = self.state_factory.create(settings)

    def reset_progress(self, state=None):
        self.state_factory.reset(state or self.state, self.settings)

    def update(self):
        if self._can_advance_gameplay():
            self._advance_gameplay()

        self._reset_after_game_over_delay()

    def _can_advance_gameplay(self):
        return (
            self.state.game_over_started_at is None
            and not self.main_menu.is_open
            and not self.data_log.is_open
            and not self.state.victory_open
        )

    def _advance_gameplay(self):
        wave_was_active = self.state.wave_manager.wave_active
        self.state.wave_manager.update(self.state.enemies, self.state.path)
        self.state.enemies.update()
        self.state.towers.update(self.state.enemies, self.state.projectiles)
        self.state.projectiles.update()

        self._resolve_enemies()
        self._finish_wave_if_cleared(wave_was_active)
        self._open_victory_if_complete()
        self._remove_inactive_projectiles()
        self._start_game_over_if_dead()

    def _resolve_enemies(self):
        for enemy in list(self.state.enemies):
            if enemy.reached_end and not enemy.metal_collected:
                self.state.player_health -= enemy.metal_reward
                enemy.metal_collected = True
            elif not enemy.alive and not enemy.metal_collected:
                self.state.metal += enemy.metal_reward
                self.state.enemies_killed += 1
                enemy.metal_collected = True
                audio.play_random_explosion()

            if not enemy.alive:
                self.state.enemies.remove(enemy)

    def _finish_wave_if_cleared(self, wave_was_active):
        self.state.wave_manager.check_cleared_wave(self.state.enemies)
        if wave_was_active and not self.state.wave_manager.wave_active:
            audio.play_sfx("wave_over")

    def _open_victory_if_complete(self):
        if not self.state.wave_manager.all_waves_complete:
            return

        self.state.victory_open = True
        self.radial_menu.close()
        self.main_menu.close()

    def _remove_inactive_projectiles(self):
        for projectile in list(self.state.projectiles):
            if not projectile.active:
                self.state.projectiles.remove(projectile)

    def _start_game_over_if_dead(self):
        if self.state.player_health > 0:
            return

        self.state.player_health = 0
        self.state.game_over_started_at = pygame.time.get_ticks()
        audio.play_sfx("game_over")
        self.radial_menu.close()
        self.main_menu.close()

    def _reset_after_game_over_delay(self):
        if self.state.game_over_started_at is None:
            return

        elapsed_time = pygame.time.get_ticks() - self.state.game_over_started_at
        if elapsed_time < GAME_OVER_RESET_DELAY_MS:
            return

        self.reset_progress()
        self.data_log.reset()
