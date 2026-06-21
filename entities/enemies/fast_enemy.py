from entities.enemies.enemy import Enemy
from systems.tags import HIGH_TECH

class FastEnemy(Enemy):
    tags = [HIGH_TECH]
    health = 100
    speed = 4
    metal_reward = 15
    sprite_file = "Fast_Robot.png"
    info = "A light, agile machine. Casted titanium frame, newest alloys, the most efficient servomotors in the sector... Still, this means the components inside are quite suseptible to overheating from laser fire."

    def __init__(self, path):
        super().__init__(
            path=path,
            health=self.health,
            speed=self.speed,
            metal_reward=self.metal_reward,
            sprite_file=self.sprite_file
        )
