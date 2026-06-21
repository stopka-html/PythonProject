from entities.enemies.enemy import Enemy
from systems.tags import MASS_PRODUCED

class BasicEnemy(Enemy):
    tags = [MASS_PRODUCED]
    health = 200
    speed = 2
    metal_reward = 10
    sprite_file = "Robot.png"
    info = "The most common type of attacker. Still, it shouldn't be underestimated, its durability is the best for it's weight class, and the cheap price means there never is only one of them."

    def __init__(self, path):
        super().__init__(
            path=path,
            health=self.health,
            speed=self.speed,
            metal_reward=self.metal_reward,
            sprite_file=self.sprite_file
        )
