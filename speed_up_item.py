import pygame
import math
import config
from base_item import BaseItem

class SpeedUpItem(BaseItem):
    """
    雲の上に出現するスピードアップアイテムを管理するクラス。
    取得するとバードの速度が上昇する。
    """
    def __init__(self, parent_cloud=None, position=None):
        super().__init__(parent_cloud, position, config.SPEED_UP_ITEM_SIZE)
        self.color = config.SPEED_UP_ITEM_COLOR
        self.outline_color = config.SPEED_UP_ITEM_OUTLINE_COLOR
        self.angle = 0
        self.update()

    def update(self):
        # 親クラスのupdateを呼び出して、位置を更新
        super().update()
        # このアイテム固有のアニメーション（回転）を追加
        self.angle = (self.angle + 1) % 360 # ゆっくり回転

    def draw(self, screen):
        """星形を描画する"""
        points = []
        current_size = self.size * self.current_scale
        for i in range(5 * 2):
            radius = current_size / 2 if i % 2 == 0 else current_size / 4
            angle = math.radians(self.angle + i * 36)
            points.append((self.pos.x + radius * math.cos(angle), self.pos.y + radius * math.sin(angle)))
        pygame.draw.polygon(screen, self.color, points)
        if config.SPEED_UP_ITEM_OUTLINE_WIDTH > 0:
            pygame.draw.polygon(screen, self.outline_color, points, config.SPEED_UP_ITEM_OUTLINE_WIDTH)