from pathlib import Path

import pygame


INFO_FILE = Path(__file__).resolve().parents[1] / "utils" / "info.txt"
SETTINGS_FILE = Path(__file__).resolve().parents[1] / "utils" / "settings.py"
VOLUME_SETTINGS = ("EFFECTS_VOLUME", "MUSIC_VOLUME")


class MainMenu:

    def __init__(self, screen_width, screen_height, settings_values):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings_values = settings_values
        self.is_open = False
        self.panel = None
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        main_button_width = max(130, int(screen_width * 0.125))
        main_button_height = max(32, int(screen_height * 0.042))
        self.main_button_rect = pygame.Rect(
            0,
            int(screen_height * 0.072),
            main_button_width,
            main_button_height
        )
        self.main_button_rect.centerx = screen_width // 2
        overlay_width = int(screen_width * 0.68)
        overlay_height = int(screen_height * 0.72)
        self.overlay_rect = pygame.Rect(0, 0, overlay_width, overlay_height)
        self.overlay_rect.center = (screen_width // 2, screen_height // 2)
        self.settings_button = pygame.Rect(0, 0, 1, 1)
        self.restart_button = pygame.Rect(0, 0, 1, 1)
        self.info_button = pygame.Rect(0, 0, 1, 1)
        self.close_button = pygame.Rect(0, 0, 1, 1)
        self.setting_buttons = []
        self.volume_sliders = {}
        self.dragging_slider = None
        self.info_text = self._load_info_text()
        self._layout_buttons()

    def toggle(self):
        self.is_open = not self.is_open
        if not self.is_open:
            self.panel = None

    def open(self):
        self.is_open = True
        self.panel = None

    def close(self):
        self.is_open = False
        self.panel = None

    def main_button_contains(self, mouse_pos):
        return self.main_button_rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        if self.main_button_contains(mouse_pos):
            self.toggle()
            return None

        if not self.is_open:
            return None

        if self.close_button.collidepoint(mouse_pos):
            self.close()
            return None

        if self.settings_button.collidepoint(mouse_pos):
            self.panel = "settings"
            return None

        if self.restart_button.collidepoint(mouse_pos):
            self.close()
            return "restart"

        if self.info_button.collidepoint(mouse_pos):
            self.panel = "info"
            return None

        if self.panel == "settings":
            if self._change_volume_from_mouse(mouse_pos):
                return "settings_changed"

            for setting_name, delta, rect in self.setting_buttons:
                if rect.collidepoint(mouse_pos):
                    self._change_setting(setting_name, delta)
                    return "settings_changed"

        return None

    def handle_mouse_motion(self, mouse_pos):
        if self.dragging_slider is None:
            return None

        if self._set_volume_from_mouse(self.dragging_slider, mouse_pos):
            return "settings_changed"

        return None

    def handle_mouse_up(self):
        self.dragging_slider = None

    def draw_button(self, screen):
        self._draw_rect_button(
            screen,
            self.main_button_rect,
            "Main Menu",
            (45, 45, 55),
            (150, 175, 195)
        )

    def draw_overlay(self, screen):
        if not self.is_open:
            return

        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 145))
        screen.blit(shade, (0, 0))

        pygame.draw.rect(
            screen,
            (32, 36, 44),
            self.overlay_rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            (155, 180, 205),
            self.overlay_rect,
            width=2,
            border_radius=8
        )

        self._draw_text(
            screen,
            "Main Menu",
            (self.overlay_rect.x + 24, self.overlay_rect.y + 20),
            (255, 255, 255),
            self.font
        )
        self._draw_rect_button(
            screen,
            self.close_button,
            "X",
            (70, 52, 56),
            (225, 130, 140)
        )
        self._draw_rect_button(
            screen,
            self.settings_button,
            "Settings",
            (48, 58, 70),
            (150, 175, 205)
        )
        self._draw_rect_button(
            screen,
            self.restart_button,
            "Restart",
            (62, 54, 48),
            (225, 180, 130)
        )
        self._draw_rect_button(
            screen,
            self.info_button,
            "Info",
            (48, 62, 56),
            (150, 210, 175)
        )

        if self.panel == "settings":
            self._draw_settings_panel(screen)
        elif self.panel == "info":
            self._draw_info_panel(screen)

    def _layout_buttons(self):
        margin = int(self.overlay_rect.width * 0.04)
        nav_width = int(self.overlay_rect.width * 0.28)
        button_height = int(self.overlay_rect.height * 0.085)
        gap = int(self.overlay_rect.height * 0.03)
        left = self.overlay_rect.x + margin
        top = self.overlay_rect.y + int(self.overlay_rect.height * 0.2)
        button_size = (nav_width, button_height)
        self.settings_button.size = button_size
        self.restart_button.size = button_size
        self.info_button.size = button_size
        self.settings_button.topleft = (left, top)
        self.restart_button.topleft = (left, top + gap)
        self.restart_button.top = self.settings_button.bottom + gap
        self.info_button.topleft = (left, self.restart_button.bottom + gap)
        close_size = max(28, int(self.overlay_rect.width * 0.04))
        self.close_button.size = (close_size, close_size)
        self.close_button.topright = (
            self.overlay_rect.right - margin,
            self.overlay_rect.y + margin
        )
        self._layout_setting_buttons()

    def _layout_setting_buttons(self):
        self.setting_buttons = []
        panel_x = self._content_left()
        y = self.overlay_rect.y + int(self.overlay_rect.height * 0.23)
        button_size = max(28, int(self.overlay_rect.height * 0.052))
        plus_x = self.overlay_rect.right - int(self.overlay_rect.width * 0.08)

        for setting_name in self._stepper_settings():
            minus_rect = pygame.Rect(panel_x, y, button_size, button_size)
            plus_rect = pygame.Rect(plus_x, y, button_size, button_size)
            self.setting_buttons.append((setting_name, -1, minus_rect))
            self.setting_buttons.append((setting_name, 1, plus_rect))
            y += int(self.overlay_rect.height * 0.12)

    def _draw_settings_panel(self, screen):
        panel_x = self._content_left()
        y = self.overlay_rect.y + int(self.overlay_rect.height * 0.13)
        self._draw_text(
            screen,
            "Settings",
            (panel_x, y),
            (255, 255, 255),
            self.small_font
        )

        y += int(self.overlay_rect.height * 0.08)
        button_size = max(28, int(self.overlay_rect.height * 0.052))
        value_x = self.overlay_rect.right - int(self.overlay_rect.width * 0.18)
        plus_x = self.overlay_rect.right - int(self.overlay_rect.width * 0.08)
        row_gap = int(self.overlay_rect.height * 0.12)

        for setting_name in self._stepper_settings():
            value = self.settings_values[setting_name]
            self._draw_text(
                screen,
                self._format_setting_name(setting_name),
                (panel_x + button_size + 12, y + 4),
                (205, 220, 235),
                self.small_font
            )
            value_text = self.small_font.render(
                str(value),
                True,
                (255, 255, 255)
            )
            value_rect = value_text.get_rect(
                center=(value_x, y + button_size // 2)
            )
            screen.blit(value_text, value_rect)

            minus_rect = pygame.Rect(panel_x, y, button_size, button_size)
            plus_rect = pygame.Rect(plus_x, y, button_size, button_size)
            self._draw_rect_button(
                screen,
                minus_rect,
                "-",
                (52, 52, 60),
                (150, 175, 195)
            )
            self._draw_rect_button(
                screen,
                plus_rect,
                "+",
                (52, 52, 60),
                (150, 175, 195)
            )
            y += row_gap

        y += int(self.overlay_rect.height * 0.035)
        self._draw_text(
            screen,
            "Sound",
            (panel_x, y),
            (255, 255, 255),
            self.small_font
        )
        y += int(self.overlay_rect.height * 0.06)
        self._draw_volume_sliders(screen, panel_x, y)

        self._layout_setting_buttons()

    def _draw_volume_sliders(self, screen, panel_x, y):
        self.volume_sliders = {}
        label_width = int(self.overlay_rect.width * 0.19)
        track_width = int(self.overlay_rect.width * 0.25)
        track_height = 6
        row_gap = int(self.overlay_rect.height * 0.105)
        track_x = panel_x + label_width
        value_x = track_x + track_width + 44

        for setting_name in VOLUME_SETTINGS:
            value = self.settings_values.get(setting_name, 100)
            label = self._format_setting_name(setting_name)
            track_rect = pygame.Rect(
                track_x,
                y + 13,
                track_width,
                track_height
            )
            knob_x = track_rect.left + int(track_rect.width * value / 100)
            knob_rect = pygame.Rect(0, 0, 16, 16)
            knob_rect.center = (knob_x, track_rect.centery)

            self.volume_sliders[setting_name] = track_rect

            self._draw_text(
                screen,
                label,
                (panel_x, y + 2),
                (205, 220, 235),
                self.small_font
            )
            pygame.draw.rect(
                screen,
                (70, 78, 88),
                track_rect,
                border_radius=3
            )
            pygame.draw.rect(
                screen,
                (150, 205, 180),
                (
                    track_rect.left,
                    track_rect.top,
                    max(0, knob_x - track_rect.left),
                    track_rect.height
                ),
                border_radius=3
            )
            pygame.draw.circle(
                screen,
                (235, 245, 240),
                knob_rect.center,
                knob_rect.width // 2
            )
            pygame.draw.circle(
                screen,
                (95, 125, 110),
                knob_rect.center,
                knob_rect.width // 2,
                width=2
            )

            value_text = self.small_font.render(
                f"{value}%",
                True,
                (255, 255, 255)
            )
            value_rect = value_text.get_rect(
                midleft=(value_x, track_rect.centery)
            )
            screen.blit(value_text, value_rect)
            y += row_gap

    def _draw_info_panel(self, screen):
        panel_x = self._content_left()
        y = self.overlay_rect.y + int(self.overlay_rect.height * 0.13)
        self._draw_text(
            screen,
            "Info",
            (panel_x, y),
            (255, 255, 255),
            self.small_font
        )

        max_chars = max(30, int((self.overlay_rect.right - panel_x) / 9))
        max_lines = max(8, int(self.overlay_rect.height / 28) - 4)

        for line in self._wrap_text(self.info_text, max_chars)[:max_lines]:
            y += 24
            self._draw_text(
                screen,
                line,
                (panel_x, y),
                (205, 220, 235),
                self.small_font
            )

    def _change_setting(self, setting_name, direction):
        steps = {
            "FPS": 5,
            "GRID_SIZE": 4,
            "STARTING_METAL": 50,
            "STARTING_HEALTH": 10
        }
        minimums = {
            "FPS": 15,
            "GRID_SIZE": 24,
            "STARTING_METAL": 0,
            "STARTING_HEALTH": 10
        }
        maximums = {
            "FPS": 240,
            "GRID_SIZE": 128,
            "STARTING_METAL": 9999,
            "STARTING_HEALTH": 999
        }

        value = self.settings_values[setting_name]
        value += steps.get(setting_name, 1) * direction
        value = max(minimums.get(setting_name, 0), value)
        value = min(maximums.get(setting_name, value), value)
        self.settings_values[setting_name] = value
        self._save_settings_file()

    def _change_volume_from_mouse(self, mouse_pos):
        for setting_name, track_rect in self.volume_sliders.items():
            hit_rect = track_rect.inflate(18, 22)
            if hit_rect.collidepoint(mouse_pos):
                self.dragging_slider = setting_name
                return self._set_volume_from_mouse(setting_name, mouse_pos)

        return False

    def _set_volume_from_mouse(self, setting_name, mouse_pos):
        track_rect = self.volume_sliders.get(setting_name)
        if track_rect is None:
            return False

        relative_x = mouse_pos[0] - track_rect.left
        value = round(max(0, min(track_rect.width, relative_x)) / track_rect.width * 100)
        if self.settings_values.get(setting_name) == value:
            return False

        self.settings_values[setting_name] = value
        self._save_settings_file()
        return True

    def _stepper_settings(self):
        return [
            setting_name
            for setting_name in self.settings_values
            if setting_name not in VOLUME_SETTINGS
        ]

    def _format_setting_name(self, setting_name):
        return setting_name.replace("_", " ").title()

    def _content_left(self):
        return self.overlay_rect.x + int(self.overlay_rect.width * 0.38)

    def _save_settings_file(self):
        if not SETTINGS_FILE.exists():
            return

        lines = SETTINGS_FILE.read_text(encoding="utf-8").splitlines()
        updated_lines = []

        for line in lines:
            updated = False

            for setting_name, value in self.settings_values.items():
                if line.startswith(f"{setting_name} ="):
                    updated_lines.append(f"{setting_name} = {value}")
                    updated = True
                    break

            if not updated:
                updated_lines.append(line)

        SETTINGS_FILE.write_text(
            "\n".join(updated_lines) + "\n",
            encoding="utf-8"
        )

    def _draw_rect_button(
        self,
        screen,
        rect,
        text,
        fill_color,
        outline_color
    ):
        pygame.draw.rect(
            screen,
            fill_color,
            rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            outline_color,
            rect,
            width=2,
            border_radius=6
        )
        text_surface = self.small_font.render(
            text,
            True,
            (255, 255, 255)
        )
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def _draw_text(self, screen, text, position, color, font):
        surface = font.render(text, True, color)
        screen.blit(surface, position)

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

    def _load_info_text(self):
        if not INFO_FILE.exists():
            return ""

        return INFO_FILE.read_text(encoding="utf-8").strip()
