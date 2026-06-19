import math
from pathlib import Path

import pygame

from entities.projectiles.laser import LaserProjectile
from entities.projectiles.projectile import Projectile
from systems import audio
from systems.tags import get_matching_tags


ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"


class Tower(pygame.sprite.Sprite):
    loaded_sprites = {}
    base_sprite_file = "Turret_Base.png"
    cannon_sprite_file = None
    sprite_scale = 1.0
    sprite_angle_offset = 0
    tags = []
    tag_damage_modifiers = {}
    projectile_type = "projectile"
    fire_sound = None

    def __init__(
        self,
        grid_x,
        grid_y,
        damage,
        range_radius,
        fire_rate,
        cost
    ):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y

        self.x = grid_x
        self.y = grid_y

        self.damage = damage
        self.range = range_radius

        self.fire_rate = fire_rate
        self.cost = cost
        self.tags = list(self.tags)
        self.tag_damage_modifiers = dict(self.tag_damage_modifiers)

        self.cooldown = 0
        self.angle = 0
        self.base_sprite = self.load_sprite(self.base_sprite_file)
        self.cannon_sprite = self.load_sprite(self.cannon_sprite_file)
        self.image = None
        self.rect = None
        self._refresh_image()

    @classmethod
    def load_sprite(cls, sprite_file):
        if sprite_file is None:
            return None

        if sprite_file not in cls.loaded_sprites:
            image = pygame.image.load(ASSET_DIR / sprite_file).convert_alpha()
            cls.loaded_sprites[sprite_file] = image

        return cls.loaded_sprites[sprite_file]

    def get_target(self, enemies):

        closest = None
        closest_distance = float("inf")

        for enemy in enemies:

            if not enemy.alive:
                continue

            distance = math.hypot(
                enemy.x - self.x,
                enemy.y - self.y
            )

            if distance <= self.range:

                if distance < closest_distance:
                    closest_distance = distance
                    closest = enemy

        return closest

    def update(self, enemies, projectiles):

        if self.cooldown > 0:
            self.cooldown -= 1

        target = self.get_target(enemies)

        if target:
            self.angle = -math.degrees(
                math.atan2(target.y - self.y, target.x - self.x)
            ) - 90

        if target and self.cooldown <= 0:

            projectiles.add(
                self.create_projectile(target)
            )

            self.cooldown = self.fire_rate
        self._refresh_image()

    def create_projectile(self, target):
        if self.projectile_type == "laser":
            projectile = LaserProjectile(
                self.get_projectile_start_point(target),
                self.get_projectile_end_point(target),
                target,
                self.get_damage_against(target)
            )
            self.play_fire_sound()
            return projectile

        start_x, start_y = self.get_projectile_start_point(target)
        projectile = Projectile(
            start_x,
            start_y,
            target,
            self.get_damage_against(target),
            8
        )
        self.play_fire_sound()
        return projectile

    def play_fire_sound(self):
        if self.fire_sound:
            audio.play_sfx(self.fire_sound)

    def get_projectile_start_point(self, target):
        return (int(self.x), int(self.y))

    def get_offset_projectile_start_point(
        self,
        target,
        forward_offset,
        side_offset=0
    ):
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            aim_radians = math.radians(-self.angle - 90)
            forward_x = math.cos(aim_radians)
            forward_y = math.sin(aim_radians)
        else:
            forward_x = dx / distance
            forward_y = dy / distance

        side_x = -forward_y
        side_y = forward_x

        return (
            int(round(
                self.x + forward_x * forward_offset + side_x * side_offset
            )),
            int(round(
                self.y + forward_y * forward_offset + side_y * side_offset
            ))
        )

    def get_projectile_end_point(self, target):
        return (int(target.x), int(target.y))

    def get_damage_against(self, enemy):
        bonus_damage = sum(
            self.tag_damage_modifiers.get(tag, 0)
            for tag in get_matching_tags(
                self.tags,
                getattr(enemy, "tags", [])
            )
        )

        return self.damage + bonus_damage

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def _refresh_image(self):
        base = self._scaled_sprite(self.base_sprite) if self.base_sprite else None
        cannon = self._scaled_sprite(self.cannon_sprite) if self.cannon_sprite else None

        base_w = base.get_width() if base else 0
        base_h = base.get_height() if base else 0
        cannon_w = cannon.get_width() if cannon else 0
        cannon_h = cannon.get_height() if cannon else 0

        rotated_cannon = None
        if cannon:
            rotated_cannon = pygame.transform.rotate(
                cannon,
                self.angle + self.sprite_angle_offset
            )
            cannon_w = rotated_cannon.get_width()
            cannon_h = rotated_cannon.get_height()

        width = max(base_w, cannon_w, 1)
        height = max(base_h, cannon_h, 1)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        if base:
            base_rect = base.get_rect(center=(width // 2, height // 2))
            self.image.blit(base, base_rect)

        if rotated_cannon:
            cannon_rect = rotated_cannon.get_rect(center=(width // 2, height // 2))
            self.image.blit(rotated_cannon, cannon_rect)

        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _scaled_sprite(self, sprite):
        if self.sprite_scale == 1.0:
            return sprite

        width, height = sprite.get_size()
        return pygame.transform.smoothscale(
            sprite,
            (
                max(1, int(width * self.sprite_scale)),
                max(1, int(height * self.sprite_scale))
            )
        )
