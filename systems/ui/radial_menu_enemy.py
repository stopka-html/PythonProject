from entities.enemies.basic_enemy import BasicEnemy
from entities.enemies.fast_enemy import FastEnemy
from entities.enemies.tank_enemy import TankEnemy
from systems.ui.radial_menu import RadialMenuOption


def create_enemy_option(label, enemy_class, color):
    return RadialMenuOption(
        label,
        color,
        icon_path=f"assets/{enemy_class.sprite_file}",
        value_text=f"{enemy_class.health} HP",
        stats=[
            f"Health: {enemy_class.health}",
            f"Speed: {enemy_class.speed}",
            f"Metal drop: {enemy_class.metal_reward}",
            f"Tags: {', '.join(enemy_class.tags)}"
        ],
        info_text=enemy_class.info
    )


def create_enemy_options():
    return [
        create_enemy_option(
            "Basic",
            BasicEnemy,
            (170, 85, 85)
        ),
        create_enemy_option(
            "Fast",
            FastEnemy,
            (180, 155, 70)
        ),
        create_enemy_option(
            "Tank",
            TankEnemy,
            (125, 125, 145)
        )
    ]
