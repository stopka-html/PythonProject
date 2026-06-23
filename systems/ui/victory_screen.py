import pygame


VICTORY_LORE_MESSAGE = (
    "victory lore message pending\n\n"
    "dont bully me"
)


class VictoryScreen:

    def __init__(self, screen_width, screen_height):
        self.title_font = pygame.font.SysFont(None, 74)
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)

        panel_width = int(screen_width * 0.64)
        panel_height = int(screen_height * 0.62)
        self.panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        self.panel_rect.center = (screen_width // 2, screen_height // 2)

        button_width = max(150, int(screen_width * 0.13))
        button_height = max(38, int(screen_height * 0.052))
        self.restart_button = pygame.Rect(0, 0, button_width, button_height)
        self.restart_button.centerx = self.panel_rect.centerx
        self.restart_button.bottom = self.panel_rect.bottom - 34

    def restart_contains(self, mouse_pos):
        return self.restart_button.collidepoint(mouse_pos)

    def draw(self, screen):
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        screen.blit(shade, (0, 0))

        pygame.draw.rect(
            screen,
            (30, 38, 36),
            self.panel_rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            (130, 225, 170),
            self.panel_rect,
            width=3,
            border_radius=8
        )

        title = self.title_font.render(
            "Victory",
            True,
            (175, 255, 205)
        )
        title_rect = title.get_rect(
            centerx=self.panel_rect.centerx,
            top=self.panel_rect.top + 38
        )
        screen.blit(title, title_rect)

        self._draw_lore_message(screen, title_rect.bottom + 26)
        self._draw_restart_button(screen)

    def _draw_lore_message(self, screen, top):
        x = self.panel_rect.left + 54
        y = top
        max_width = self.panel_rect.width - 108
        max_height = self.restart_button.top - top - 28
        font, line_height, lines = self._fit_message_lines(
            max_width,
            max_height
        )

        for line in lines:
            if line:
                text = font.render(
                    line,
                    True,
                    (225, 238, 230)
                )
                screen.blit(text, (x, y))

            y += line_height

    def _draw_restart_button(self, screen):
        pygame.draw.rect(
            screen,
            (48, 68, 56),
            self.restart_button,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            (150, 230, 175),
            self.restart_button,
            width=2,
            border_radius=6
        )

        label = self.small_font.render(
            "Restart",
            True,
            (255, 255, 255)
        )
        label_rect = label.get_rect(center=self.restart_button.center)
        screen.blit(label, label_rect)

    def _fit_message_lines(self, max_width, max_height):
        for font_size in range(28, 17, -1):
            font = pygame.font.SysFont(None, font_size)
            line_height = font.get_linesize() + 2
            lines = self._message_lines(max_width, font)

            if len(lines) * line_height <= max_height:
                self.font = font
                return font, line_height, lines

        font = pygame.font.SysFont(None, 18)
        self.font = font
        return font, font.get_linesize(), self._message_lines(max_width, font)

    def _message_lines(self, max_width, font):
        lines = []

        for paragraph in VICTORY_LORE_MESSAGE.split("\n"):
            if paragraph:
                lines.extend(self._wrap_text(paragraph, max_width, font))
            else:
                lines.append("")

        return lines

    def _wrap_text(self, text, max_width, font):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = word if not current_line else f"{current_line} {word}"

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
