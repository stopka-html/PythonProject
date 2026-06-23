import pygame


class GameOverScreen:

    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 30)

    def draw(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("Game Over", True, (255, 90, 90))
        title_rect = title.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 - 28)
        )
        screen.blit(title, title_rect)

        subtitle = self.small_font.render(
            "Resetting progress...",
            True,
            (235, 235, 245)
        )
        subtitle_rect = subtitle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 32)
        )
        screen.blit(subtitle, subtitle_rect)
