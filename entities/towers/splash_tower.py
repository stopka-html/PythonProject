from entities.towers.tower import Tower
from systems.tags import ARMORED, HIGH_TECH


class SplashTower(Tower):
    cannon_sprite_file = "Cannon_Turret_Launcher.png"
    fire_sound = "cannon_turret"
    projectile_forward_offset = 22
    barrel_side_offset = 6
    tags = [ARMORED]
    tag_damage_modifiers = {
        ARMORED: 40,
        HIGH_TECH: -10
    }
    cost = 120
    damage = 50
    range_radius = 160
    fire_rate = 60
    info = "The Tartarus.Co Chemical Ablation Unit, also dubbed the Splash cannon, is a simple asteriod clearing implement that fires a self-propelled chemcical payload to melt rock. Today, hovewer, it will melt the frames of the enemy."

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            damage=self.damage,
            range_radius=self.range_radius,
            fire_rate=self.fire_rate,
            cost=self.cost
        )
        self.next_barrel_side = -1

    def get_projectile_start_point(self, target):
        side_offset = self.barrel_side_offset * self.next_barrel_side
        self.next_barrel_side *= -1

        return self.get_offset_projectile_start_point(
            target,
            self.projectile_forward_offset,
            side_offset
        )
