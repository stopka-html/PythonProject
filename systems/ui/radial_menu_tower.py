from entities.towers.basic_tower import BasicTower
from entities.towers.sniper_tower import SniperTower
from entities.towers.splash_tower import SplashTower
from systems.ui.radial_menu import RadialMenuOption


def create_tower_option(label, tower_class, color, icon_path, enabled=True):
    modifier_stats = [
        f"{tag}: {modifier:+} damage"
        for tag, modifier in tower_class.tag_damage_modifiers.items()
    ]

    if not modifier_stats:
        modifier_stats = ["Modifiers: None"]

    return RadialMenuOption(
        label,
        color,
        icon_path=icon_path,
        value_text=str(tower_class.cost),
        stats=[
            f"Cost: {tower_class.cost} metal",
            f"Damage: {tower_class.damage}",
            f"Range: {tower_class.range_radius}",
            f"Fire rate: {tower_class.fire_rate}",
            *modifier_stats
        ],
        info_text=tower_class.info,
        payload=tower_class,
        enabled=enabled
    )


def create_build_options():
    return [
        create_tower_option(
            "Basic",
            BasicTower,
            (55, 120, 210),
            "assets/Gatling_Turret_Laser.png"
        ),
        create_tower_option(
            "Splash",
            SplashTower,
            (205, 120, 55),
            "assets/Cannon_Turret_Launcher.png"
        ),
        create_tower_option(
            "Sniper",
            SniperTower,
            (105, 190, 130),
            "assets/Sniper_Turret_Laser.png"
        )
    ]


def create_affordable_build_options(build_options, metal):
    return [
        create_tower_option(
            option.label,
            option.payload,
            option.color,
            option.icon_path,
            enabled=metal >= option.payload.cost
        )
        for option in build_options
    ]
