from entities.enemies.enemy import Enemy
from systems.tags import ARMORED

class TankEnemy(Enemy):
    tags = [ARMORED]
    health = 750
    speed = 1
    metal_reward = 25
    sprite_file = "Armored_Robot.png"
    info = "A heavy, nearly-mech grade machine. This one's heat shielding can withstand atmospheric re-etry temps. Heavier arnaments will be needed to get through its shell... Or a sufficient quantity of lighter ones."

    def __init__(self, path):
        super().__init__(
            path,
            health=self.health,
            speed=self.speed,
            metal_reward=self.metal_reward,
            sprite_file=self.sprite_file
        )
