import pygame
import math
import config
from base_item import BaseItem

class HeartItem(BaseItem):
    """
    雲の上に出現するハートアイテムを管理するクラス。
    取得するとタワーを修復する効果を持つ。
    """
    def __init__(self, parent_cloud=None, position=None):
        # 親クラスの初期化を呼び出し、共通の属性を設定
        super().__init__(parent_cloud, position, config.HEART_ITEM_SIZE)
        # このアイテム固有の属性を設定
        self.color = config.HEART_ITEM_COLOR
        self.update()

    def draw(self, screen):
        """
        ハートを画面に描画する。main.pyのdraw_heart関数をベースに作成。
        """
        points = []
        center_x, center_y = self.pos.x, self.pos.y
        current_size = self.size * self.current_scale

        for t_deg in range(0, 360):
            t_rad = math.radians(t_deg)
            scale = current_size / 32.0

            dx = 16 * (math.sin(t_rad) ** 3)
            dy = -(13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))

            x = center_x + dx * scale
            y = center_y + dy * scale
            points.append((x, y))

        pygame.draw.polygon(screen, self.color, points)
        if config.HEART_ITEM_OUTLINE_WIDTH > 0:
            pygame.draw.polygon(screen, config.BLACK, points, config.HEART_ITEM_OUTLINE_WIDTH)