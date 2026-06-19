import pygame
import math

class Projectile(pygame.sprite.Sprite):

    def __init__(self, x, y, target, damage, speed):
        super().__init__()
        self.x = x
        self.y = y

        self.target = target

        self.damage = damage
        self.speed = speed

        self.active = True
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (4, 4), 4)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        if not self.target.alive:
            self.active = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y

        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.target.take_damage(self.damage)
            self.active = False
            return

        self.x += dx / distance * self.speed
        self.y += dy / distance * self.speed
        self.rect.center = (int(self.x), int(self.y))
