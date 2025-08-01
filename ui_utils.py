import pygame
import math

def draw_text(screen, text, font, color, center_pos, outline_color=None, outline_width=0, alpha=None):
    """
    指定された位置に中央揃えでアウトライン付きテキストを描画する。
    アルファ（透明度）も指定可能。
    """
    # アウトラインの描画
    if outline_color and outline_width > 0:
        outline_surface = font.render(text, True, outline_color)
        if alpha is not None:
            outline_surface.set_alpha(alpha)
        # 8方向にオフセットして描画
        offsets = [
            (dx, dy) for dx in range(-outline_width, outline_width + 1, outline_width)
                     for dy in range(-outline_width, outline_width + 1, outline_width)
                     if not (dx == 0 and dy == 0)
        ]
        for dx, dy in offsets:
            outline_rect = outline_surface.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
            screen.blit(outline_surface, outline_rect)

    # 本体のテキストを描画
    text_surface = font.render(text, True, color)
    if alpha is not None:
        text_surface.set_alpha(alpha)
    text_rect = text_surface.get_rect(center=center_pos)
    screen.blit(text_surface, text_rect)

def draw_heart(screen, center_x, center_y, size, color):
    """指定された位置にハートを描画する。"""
    points = []
    for t_deg in range(0, 360):
        t_rad = math.radians(t_deg)
        scale = size / 32.0
        dx = 16 * (math.sin(t_rad) ** 3)
        dy = -(13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
        x = center_x + dx * scale
        y = center_y + dy * scale
        points.append((x, y))
    pygame.draw.polygon(screen, color, points)