from types import SimpleNamespace

from systems.game_reset import GameReset


class GameStateFactory:

    def __init__(self, width, height, waves):
        self.game_reset = GameReset(width, height, waves)

    def create(self, settings):
        state = self.game_reset.create_state(
            settings["STARTING_METAL"],
            settings["STARTING_HEALTH"],
            settings["GRID_SIZE"]
        )
        return SimpleNamespace(
            **state,
            game_over_started_at=None,
            victory_open=False
        )

    def reset(self, state, settings):
        fresh_state = self.create(settings)
        state.__dict__.clear()
        state.__dict__.update(fresh_state.__dict__)
