import math

import pygame

import systems.ui.baseUI


DATA_LOG_MESSAGE = (
    "DATA LOG 044-F\n\n"

    "Our extinction draws near.\n"
    "The age of intergalactic travel is over. IT has gone rogue, and our ways of the world are over.\n"
    "The project was always hubris. We were too foolish to ever realize it.\n"
    "All core worlds are lost. The gates can never take us far enough to escape.\n"
    "The others went on the arc. We are alone here. But the beacon must stay standing, their FTL's will not take them far otherwise.\n\n"

    "We have to die to make sure the others escape.\n\n"

    "Praetorian: Initiate the combat simulations. We have to hold out until they jump.\n"
    "<PULLLING DATA_STREAM>\n\n"
    "<RECOVERING SYSTEM_CONFIG>\n\n"
    "<INITIALISING_SIMULATION>\n\n"
    "<BOOTING_UP CORE//DESIGNATION:*praetorian*>\n\n"
    "<system online>\n"
    "<combat simulation in progress>\n"
)


class DataLog(systems.ui.baseUI.BaseUI):

    def __init__(self, screen_width, screen_height):
        # super().__init__(0,0,0)
        self.font = pygame.font.SysFont(None, 22)
        self.title_font = pygame.font.SysFont(None, 54)
        self.small_font = pygame.font.SysFont(None, 24)

        button_width = max(150, int(screen_width * 0.13))
        button_height = max(34, int(screen_height * 0.045))
        self.button_rect = pygame.Rect(0, 0, button_width, button_height)
        self.button_rect.centerx = screen_width // 2
        self.button_rect.top = int(screen_height * 0.12)

        panel_width = int(screen_width * 0.72)
        panel_height = int(screen_height * 0.74)
        self.panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        self.panel_rect.center = (screen_width // 2, screen_height // 2)

        close_width = max(120, int(screen_width * 0.11))
        close_height = max(34, int(screen_height * 0.045))
        self.close_rect = pygame.Rect(0, 0, close_width, close_height)
        self.close_rect.centerx = self.panel_rect.centerx
        self.close_rect.bottom = self.panel_rect.bottom - 28

        self._is_open = False
        self._is_dissmissed = False

    def button_contains(self, mouse_pos):
        return self.button_rect.collidepoint(mouse_pos)

    def close_contains(self, mouse_pos):
        return self.close_rect.collidepoint(mouse_pos)

    def draw_button(self, screen, ticks):
        pulse = (math.sin(ticks * 0.012) + 1) / 2
        fill_color = (
            120 + int(105 * pulse),
            18 + int(20 * pulse),
            24 + int(20 * pulse)
        )
        outline_color = (
            255,
            90 + int(90 * pulse),
            95 + int(70 * pulse)
        )

        pygame.draw.rect(
            screen,
            fill_color,
            self.button_rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            outline_color,
            self.button_rect,
            width=2,
            border_radius=6
        )

        label = self.small_font.render(
            "DATA LOG",
            True,
            (255, 245, 245)
        )
        label_rect = label.get_rect(center=self.button_rect.center)
        screen.blit(label, label_rect)

    def draw_panel(self, screen):

        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        screen.blit(shade, (0, 0))

        pygame.draw.rect(
            screen,
            (35, 30, 34),
            self.panel_rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            (235, 75, 85),
            self.panel_rect,
            width=3,
            border_radius=8
        )

        title = self.title_font.render(
            "DATA LOG",
            True,
            (255, 105, 110)
        )
        title_rect = title.get_rect(
            centerx=self.panel_rect.centerx,
            top=self.panel_rect.top + 34
        )
        screen.blit(title, title_rect)

        self._draw_message(screen, title_rect.bottom + 20)
        self._draw_close_button(screen)

    def _draw_message(self, screen, top):
        x = self.panel_rect.left + 48
        y = top
        max_width = self.panel_rect.width - 96
        max_height = self.close_rect.top - top - 24
        font, line_height, lines = self._fit_message_lines(
            max_width,
            max_height
        )

        for line in lines:
            if line:
                text = font.render(
                    line,
                    True,
                    (238, 230, 230)
                )
                screen.blit(text, (x, y))

            y += line_height

    def _draw_close_button(self, screen):
        pygame.draw.rect(
            screen,
            (75, 38, 44),
            self.close_rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            (235, 100, 110),
            self.close_rect,
            width=2,
            border_radius=6
        )

        label = self.small_font.render(
            "Dismiss",
            True,
            (255, 245, 245)
        )
        label_rect = label.get_rect(center=self.close_rect.center)
        screen.blit(label, label_rect)


    @property
    def is_open(self):
        return self._is_open
    
    @property
    def is_dissmissed(self):
        return self._is_dissmissed

    def _fit_message_lines(self, max_width, max_height):
        for font_size in range(22, 15, -1):
            font = pygame.font.SysFont(None, font_size)
            line_height = font.get_linesize() + 1
            lines = []

            for paragraph in DATA_LOG_MESSAGE.split("\n"):
                if paragraph:
                    lines.extend(self._wrap_text(paragraph, max_width, font))
                else:
                    lines.append("")

            if len(lines) * line_height <= max_height:
                self.font = font
                return font, line_height, lines

        font = pygame.font.SysFont(None, 16)
        line_height = font.get_linesize()
        lines = []

        for paragraph in DATA_LOG_MESSAGE.split("\n"):
            if paragraph:
                lines.extend(self._wrap_text(paragraph, max_width, font))
            else:
                lines.append("")

        self.font = font
        return font, line_height, lines

    def _wrap_text(self, text, max_width, font):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            word_parts = self._split_long_word(word, max_width, font)

            for word_part in word_parts:
                current_line = self._append_wrapped_word(
                    lines,
                    current_line,
                    word_part,
                    max_width,
                    font
                )

        if current_line:
            lines.append(current_line)

        return lines

    def _append_wrapped_word(
        self,
        lines,
        current_line,
        word,
        max_width,
        font
    ):
        test_line = word if not current_line else f"{current_line} {word}"
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

        return current_line

    def _split_long_word(self, word, max_width, font):
        if font.size(word)[0] <= max_width:
            return [word]

        parts = []
        current_part = ""

        for character in word:
            test_part = f"{current_part}{character}"

            if font.size(test_part)[0] <= max_width:
                current_part = test_part
            else:
                if current_part:
                    parts.append(current_part)
                current_part = character

        if current_part:
            parts.append(current_part)

        return parts
    
    def draw(self, screen):
        if self.is_open:
            self.draw_panel(screen)
        if not self.is_open and not self.is_dissmissed:
            self.draw_button(screen, pygame.time.get_ticks())

    def update(self, *args, **kwargs):

        if self.is_open and self.is_dissmissed:
            self._is_open = False
        
        if "mouse_pos" in kwargs and self.close_contains(kwargs["mouse_pos"]) and "click" in kwargs and kwargs["click"]:
            self._is_dissmissed = True
            self._is_open = False

            return True

        if(not self.is_dissmissed and self.button_contains(pygame.mouse.get_pos()) and "click" in kwargs and kwargs["click"]):
            self._is_open = True
            return True
        return False
