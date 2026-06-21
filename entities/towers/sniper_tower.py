from entities.towers.tower import Tower
from systems.tags import HIGH_TECH
from systems.tags import ARMORED

class SniperTower(Tower):
    cannon_sprite_file = "Sniper_Turret_Laser.png"
    projectile_type = "laser"
    fire_sound = "laser_turret"
    projectile_forward_offset = 24
    tags = [HIGH_TECH]
    tag_damage_modifiers = {
        HIGH_TECH: 20,
        ARMORED: -10
    }
    cost = 90
    damage = 80
    range_radius = 500
    fire_rate = 100
    info = "MK2 Laser Cannon, an older generation of the laser gatling cannon. It by itself is just a big barely-modified laser mining aparatus, stripped straight from a mining vessel, with much pricier capacitors."

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            damage=self.damage,
            range_radius=self.range_radius,
            fire_rate=self.fire_rate,
            cost=self.cost
        )

    def get_projectile_start_point(self, target):
        return self.get_offset_projectile_start_point(
            target,
            self.projectile_forward_offset
        )
