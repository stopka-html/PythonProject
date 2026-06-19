from entities.enemies.basic_enemy import BasicEnemy
from entities.enemies.fast_enemy import FastEnemy
from entities.enemies.tank_enemy import TankEnemy


ENEMY_TYPES = {
    "basic": BasicEnemy,
    "fast": FastEnemy,
    "tank": TankEnemy
}


class WaveManager:

    def __init__(self, waves):
        self.waves = waves
        self.current_wave_index = 0
        self.spawn_queue = []
        self.spawn_timer = 0
        self.wave_active = False
        self.cleared_wave = bool(waves)
        self.all_waves_complete = False

    @property
    def current_wave_number(self):
        if not self.waves:
            return 0

        return min(
            self.current_wave_index + 1,
            len(self.waves)
        )

    def update(self, enemies, path):
        if self.all_waves_complete:
            return

        if not self.wave_active:
            self.check_cleared_wave(enemies)
            return

        if self.spawn_queue:
            self._update_spawning(enemies, path)
            return

        self.check_cleared_wave(enemies)

    def start_next_wave(self):
        if not self.cleared_wave:
            return False

        if self.current_wave_index >= len(self.waves):
            self.all_waves_complete = True
            self.cleared_wave = False
            return False

        wave = self.waves[self.current_wave_index]
        self.spawn_queue = self._build_spawn_queue(wave)
        self.spawn_timer = 0
        self.wave_active = True
        self.cleared_wave = False
        return True

    def _build_spawn_queue(self, wave):
        spawn_queue = []

        for group in wave.get("enemies", []):
            enemy_type = group["type"]
            count = group["count"]

            if enemy_type not in ENEMY_TYPES:
                raise ValueError(f"Unknown enemy type: {enemy_type}")

            spawn_queue.extend([ENEMY_TYPES[enemy_type]] * count)

        return spawn_queue

    def _update_spawning(self, enemies, path):
        wave = self.waves[self.current_wave_index]
        spawn_delay = wave.get("spawn_delay", 60)

        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            return

        enemy_class = self.spawn_queue.pop(0)
        enemies.add(enemy_class(path))
        self.spawn_timer = spawn_delay

    def check_cleared_wave(self, enemies):
        if (
            self.wave_active
            and not self.spawn_queue
            and len(enemies) == 0
        ):
            self.current_wave_index += 1
            self.wave_active = False

        self.all_waves_complete = self.current_wave_index >= len(self.waves)
        self.cleared_wave = (
            not self.all_waves_complete
            and not self.wave_active
            and not self.spawn_queue
            and len(enemies) == 0
        )
