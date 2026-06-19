import pygame


class LaserProjectile(pygame.sprite.Sprite):

    def __init__(self, start_pos, end_pos, target, damage, duration=6):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.target = target
        self.damage = damage
        self.duration = duration
        self.frames_left = duration
        self.active = True
        self.damage_applied = False
        self._refresh_image()

    def update(self):
        if not self.damage_applied:
            if self.target.alive:
                self.target.take_damage(self.damage)

            self.damage_applied = True

        self.frames_left -= 1

        if self.frames_left <= 0:
            self.active = False
        self._refresh_image()

    def _refresh_image(self):
        min_x = min(self.start_pos[0], self.end_pos[0])
        min_y = min(self.start_pos[1], self.end_pos[1])
        max_x = max(self.start_pos[0], self.end_pos[0])
        max_y = max(self.start_pos[1], self.end_pos[1])
        width = max(1, max_x - min_x + 6)
        height = max(1, max_y - min_y + 6)

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        start = (self.start_pos[0] - min_x + 3, self.start_pos[1] - min_y + 3)
        end = (self.end_pos[0] - min_x + 3, self.end_pos[1] - min_y + 3)
        pygame.draw.line(self.image, (255, 40, 40, 179), start, end, 4)
        self.rect = self.image.get_rect(
            center=(
                (self.start_pos[0] + self.end_pos[0]) // 2,
                (self.start_pos[1] + self.end_pos[1]) // 2
            )
        )
