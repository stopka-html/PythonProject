import math
import os

import pygame


class RadialMenuOption:

    def __init__(
        self,
        label,
        color,
        icon_path=None,
        value_text=None,
        stats=None,
        info_text="",
        payload=None,
        enabled=True
    ):
        self.label = label
        self.color = color
        self.icon_path = icon_path
        self.value_text = value_text
        self.stats = stats or []
        self.info_text = info_text
        self.payload = payload
        self.enabled = enabled
        self.icon = None


class RadialMenu:

    def __init__(self, options=None):
        self.options = options or []
        self.is_open = False
        self.grid_pos = None
        self.world_pos = None
        self.center = None
        self.radius = 82
        self.option_radius = 30
        self.small_font = pygame.font.SysFont(None, 18)
        self._load_icons()

    def set_options(self, options):
        self.options = options
        self._load_icons()

    def open(self, grid_pos, world_pos, screen_size, options=None):
        if options is not None:
            self.set_options(options)

        self.is_open = True
        self.grid_pos = grid_pos
        self.world_pos = world_pos
        self.center = self._clamped_center(world_pos, screen_size)

    def close(self):
        self.is_open = False
        self.grid_pos = None
        self.world_pos = None
        self.center = None

    def get_selected_option(self, mouse_pos):
        if not self.is_open:
            return None

        option = self.get_hovered_option(mouse_pos)
        if option and option.enabled:
            return option

        return None

    def get_hovered_option(self, mouse_pos):
        if not self.is_open:
            return None

        for option, center in self._option_positions():
            if self._point_distance(mouse_pos, center) <= self.option_radius:
                return option

        return None

    def contains(self, mouse_pos):
        if not self.is_open:
            return False

        if self._point_distance(mouse_pos, self.center) <= self.option_radius:
            return True

        return any(
            self._point_distance(mouse_pos, center) <= self.option_radius
            for _, center in self._option_positions()
        )

    def draw(self, screen, mouse_pos=None):
        if not self.is_open:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(
            overlay,
            (10, 14, 20, 170),
            self.center,
            self.radius + self.option_radius + 12
        )
        pygame.draw.circle(
            overlay,
            (75, 95, 115, 210),
            self.center,
            self.option_radius,
            width=2
        )

        for option, center in self._option_positions():
            self._draw_option(overlay, option, center)

        if mouse_pos:
            hovered_option = self.get_hovered_option(mouse_pos)
            if hovered_option:
                self._draw_details(overlay, hovered_option, mouse_pos)

        screen.blit(overlay, (0, 0))

    def _draw_option(self, surface, option, center):
        line_color = (110, 135, 155, 160)
        fill_color = option.color if option.enabled else (70, 70, 76)
        outline_color = (235, 245, 255) if option.enabled else (135, 135, 145)
        text_color = (255, 255, 255) if option.enabled else (165, 165, 175)
        value_color = (190, 220, 255) if option.enabled else (150, 150, 160)

        pygame.draw.line(
            surface,
            line_color,
            self.center,
            center,
            2
        )
        pygame.draw.circle(
            surface,
            fill_color,
            center,
            self.option_radius
        )
        pygame.draw.circle(
            surface,
            outline_color,
            center,
            self.option_radius,
            width=2
        )

        if option.icon:
            icon_rect = option.icon.get_rect(center=center)
            surface.blit(option.icon, icon_rect)

        label = self.small_font.render(
            option.label,
            True,
            text_color
        )
        label_rect = label.get_rect(
            center=(center[0], center[1] + self.option_radius + 12)
        )
        surface.blit(label, label_rect)

        if option.value_text:
            value = self.small_font.render(
                option.value_text,
                True,
                value_color
            )
            value_rect = value.get_rect(
                center=(center[0], center[1] - self.option_radius - 10)
            )
            surface.blit(value, value_rect)

    def _draw_details(self, surface, option, mouse_pos):
        lines = [option.label]
        lines.extend(option.stats)

        if option.info_text:
            lines.extend(self._wrap_text(option.info_text, 28))

        if len(lines) == 1:
            lines.append("No additional info")

        line_height = 20
        padding = 10
        width = 230
        height = padding * 2 + line_height * len(lines)
        x = mouse_pos[0] + 16
        y = mouse_pos[1] + 16

        if x + width > surface.get_width() - 8:
            x = mouse_pos[0] - width - 16

        if y + height > surface.get_height() - 8:
            y = surface.get_height() - height - 8

        x = max(8, x)
        y = max(8, y)
        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(
            surface,
            (18, 22, 28, 235),
            rect,
            border_radius=6
        )
        pygame.draw.rect(
            surface,
            (150, 175, 195, 230),
            rect,
            width=2,
            border_radius=6
        )

        for index, line in enumerate(lines):
            color = (255, 255, 255) if index == 0 else (205, 220, 235)
            text = self.small_font.render(line, True, color)
            surface.blit(
                text,
                (rect.x + padding, rect.y + padding + index * line_height)
            )

    def _load_icons(self):
        for option in self.options:
            if option.icon or not option.icon_path:
                continue

            if not os.path.exists(option.icon_path):
                continue

            image = pygame.image.load(option.icon_path).convert_alpha()
            option.icon = self._fit_icon(image, 34)

    def _fit_icon(self, image, max_size):
        width, height = image.get_size()
        scale = min(max_size / width, max_size / height)
        icon_size = (
            max(1, int(width * scale)),
            max(1, int(height * scale))
        )

        return pygame.transform.smoothscale(image, icon_size)

    def _wrap_text(self, text, max_chars):
        words = text.split()
        if not words:
            return []

        lines = []
        current_line = words[0]

        for word in words[1:]:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line = f"{current_line} {word}"
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def _option_positions(self):
        if not self.center:
            return []

        count = len(self.options)
        if count == 0:
            return []

        start_angle = -math.pi / 2
        step = (2 * math.pi) / count

        positions = []
        for index, option in enumerate(self.options):
            angle = start_angle + index * step
            x = self.center[0] + math.cos(angle) * self.radius
            y = self.center[1] + math.sin(angle) * self.radius
            positions.append((option, (int(x), int(y))))

        return positions

    def _clamped_center(self, world_pos, screen_size):
        padding = self.radius + self.option_radius + 24
        width, height = screen_size

        return (
            max(padding, min(width - padding, world_pos[0])),
            max(padding, min(height - padding, world_pos[1]))
        )

    def _point_distance(self, point_a, point_b):
        return math.hypot(
            point_a[0] - point_b[0],
            point_a[1] - point_b[1]
        )
