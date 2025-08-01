import pygame
import math
import config
from base_item import BaseItem

class SizeUpItem(BaseItem):
    """
    雲の上に出現する巨大化アイテムを管理するクラス。
    取得するとバードが一定時間巨大化する。
    """
    def __init__(self, parent_cloud=None, position=None):
        super().__init__(parent_cloud, position, config.SIZE_UP_ITEM_SIZE)
        self.color = config.SIZE_UP_ITEM_COLOR
        self.outline_color = config.SIZE_UP_ITEM_OUTLINE_COLOR
        # このアイテム固有の浮遊アニメーション用
        self.float_offset = 0
        self.float_direction = 1
        self.update()

    def update(self):
        # 親クラスのupdateを呼び出して、基本的な位置を更新
        super().update()
        # このアイテム固有の浮遊アニメーションを追加
        self.float_offset += self.float_direction * 0.1
        if abs(self.float_offset) > 3: self.float_direction *= -1
        self.pos.y += self.float_offset

    def draw(self, screen):
        """上向き矢印を描画する"""
        current_size = self.size * self.current_scale
        s, p = current_size / 2, self.pos
        points = [(p.x, p.y - s*0.8), (p.x + s*0.6, p.y), (p.x + s*0.2, p.y), (p.x + s*0.2, p.y + s*0.8), (p.x - s*0.2, p.y + s*0.8), (p.x - s*0.2, p.y), (p.x - s*0.6, p.y)]
        pygame.draw.polygon(screen, self.color, points)
        if config.SIZE_UP_ITEM_OUTLINE_WIDTH > 0:
            pygame.draw.polygon(screen, self.outline_color, points, config.SIZE_UP_ITEM_OUTLINE_WIDTH)