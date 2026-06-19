import pygame
import math
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
SPRITE_ANGLE_OFFSET = 90


#Here lies the enemy class, as well as checks for movement, health, damage, and enemy visuals.
#Enemy class. Among the standard paremers, this one also carries the reward for killing the enemy, and checks the relative path coorinates for spawning.
class Enemy(pygame.sprite.Sprite):
    loaded_sprites = {}
    tags = []

    def __init__(
        self,
        path,
        health,
        speed,
        metal_reward,
        sprite_file=None
    ):
        super().__init__()
        self.path = path
        self.health = health
        self.max_health = health
        self.speed = speed
        self.metal_reward = metal_reward
        self.tags = list(self.tags)
        self.sprite = self.load_sprite(sprite_file)
        self.angle = 0

        self.path_index = 0

        self.x = path[0][0]
        self.y = path[0][1]

        self.radius = 16

        self.alive = True
        self.reached_end = False
        self.metal_collected = False
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

#Simple check that controls enemy health, damage taking and status.
    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.alive = False
            self._refresh_image()

#Enemy movement check and control.
    def update(self):
        if not self.alive:
            return

        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            self.alive = False
            return

        target_x, target_y = self.path[self.path_index + 1]

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.hypot(dx, dy)

        if distance > 0:
            self.angle = -math.degrees(math.atan2(dy, dx)) - 90

#Scary movement paremeters. Does a bunch of checks with the distance between the target and the current position. The math makes my head hurt...
        if distance <= self.speed:
            self.x = target_x
            self.y = target_y
            self.path_index += 1

            if self.path_index >= len(self.path) - 1:
                self.reached_end = True
                self.alive = False
        elif distance > 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        else:
            self.path_index += 1

        self._refresh_image()

#Draws the enemy and health bar visuals.
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def _refresh_image(self):
        if self.sprite:
            rotated_sprite = pygame.transform.rotate(
                self.sprite,
                self.angle + SPRITE_ANGLE_OFFSET
            )
            width = max(rotated_sprite.get_width(), 32)
            height = rotated_sprite.get_height() + 10
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite_rect = rotated_sprite.get_rect(
                center=(width // 2, height // 2 - 4)
            )
            self.image.blit(rotated_sprite, sprite_rect)
        else:
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                self.image,
                (255, 0, 0),
                (self.radius, self.radius),
                self.radius
            )

        bar_width = 32
        health_ratio = max(0.0, self.health / self.max_health)
        bar_x = (self.image.get_width() - bar_width) // 2
        pygame.draw.rect(
            self.image,
            (255, 0, 0),
            (bar_x, 0, bar_width, 5)
        )
        pygame.draw.rect(
            self.image,
            (0, 255, 0),
            (bar_x, 0, int(bar_width * health_ratio), 5)
        )
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
