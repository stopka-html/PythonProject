import pygame

# Contains misc. UI elements seen in the game. The name is... Perhaps a bit of a missnomer. Nevertheless, I'm a little too lazy to change it now.
class Menu:

    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 26)
        button_width = max(132, int(screen_width * 0.118))
        button_height = max(36, int(screen_height * 0.05))
        self.wave_button_rect = pygame.Rect(
            0,
            int(screen_height * 0.02),
            button_width,
            button_height
        )
        self.wave_button_rect.right = screen_width - int(screen_width * 0.023)

    def wave_button_contains(self, mouse_pos):
        return self.wave_button_rect.collidepoint(mouse_pos)

    def wave_button_clicked(self, mouse_pos, can_start_wave):
        return (
            can_start_wave
            and self.wave_button_contains(mouse_pos)
        )

    def draw(
        self,
        screen,
        wave,
        enemies_killed,
        metal,
        tower_cost,
        player_health,
        can_start_wave,
        all_waves_complete
    ):
        self._draw_text(
            screen,
            f"Wave: {wave}",
            (16, 16),
            (255, 255, 255)
        )
        self._draw_text(
            screen,
            f"Killed: {enemies_killed}",
            (16, 48),
            (255, 255, 255)
        )
        self._draw_text(
            screen,
            f"Metal: {metal}",
            (16, 80),
            (190, 220, 255)
        )


        health_rect = pygame.Rect(0, 12, 150, 40)
        health_rect.centerx = screen.get_width() // 2

        pygame.draw.rect(
            screen,
            (45, 45, 55),
            health_rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            (230, 95, 95),
            health_rect,
            width=2,
            border_radius=6
        )

        health_text = self.small_font.render(
            f"Health: {player_health}",
            True,
            (255, 255, 255)
        )
        health_text_rect = health_text.get_rect(
            center=health_rect.center
        )
        screen.blit(health_text, health_text_rect)

        self._draw_wave_button(
            screen,
            can_start_wave,
            all_waves_complete
        )

    def _draw_wave_button(
        self,
        screen,
        can_start_wave,
        all_waves_complete
    ):
        if all_waves_complete:
            fill_color = (45, 45, 55)
            outline_color = (120, 120, 130)
            text_color = (170, 170, 180)
            text = "All Clear"
        elif can_start_wave:
            fill_color = (45, 70, 55)
            outline_color = (120, 220, 150)
            text_color = (255, 255, 255)
            text = "Start Wave"
        else:
            fill_color = (45, 45, 55)
            outline_color = (120, 120, 130)
            text_color = (170, 170, 180)
            text = "Wave Active"

        pygame.draw.rect(
            screen,
            fill_color,
            self.wave_button_rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            outline_color,
            self.wave_button_rect,
            width=2,
            border_radius=6
        )

        button_text = self.small_font.render(
            text,
            True,
            text_color
        )
        button_text_rect = button_text.get_rect(
            center=self.wave_button_rect.center
        )
        screen.blit(button_text, button_text_rect)

    def _draw_text(
        self,
        screen,
        text,
        position,
        color,
        font=None
    ):
        if font is None:
            font = self.font

        surface = font.render(text, True, color)
        screen.blit(surface, position)
