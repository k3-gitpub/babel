import pygame
import math
import config

class HeartItem:
    """
    雲の上に出現するハートアイテムを管理するクラス。
    取得するとタワーを修復する効果を持つ。
    """
    def __init__(self, parent_cloud):
        """
        ハートアイテムを初期化する。
        :param parent_cloud: このハートが乗る親のCloudオブジェクト
        """
        self.parent_cloud = parent_cloud
        self.size = config.HEART_ITEM_SIZE
        self.color = config.HEART_ITEM_COLOR

        # --- 親の雲の「元の形」を基準に、相対的なYオフセットを計算 ---
        # 雲を構成する元の円の中で最もY座標が小さいもの（最も上にあるもの）を探す
        original_top_y = self.parent_cloud.original_center_y
        if self.parent_cloud.original_puffs:
            # 各円の上端（中心Y + 相対Y - 半径）を計算し、その最小値を取得
            original_top_y = min(
                self.parent_cloud.original_center_y + offset.y - radius 
                for offset, radius in self.parent_cloud.original_puffs
            )
        
        # 雲の元の中心Yからの相対的なオフセットを計算して保存
        # これには設定ファイルからのオフセットも含まれる
        self.y_offset_from_center = (original_top_y + config.HEART_ITEM_Y_OFFSET) - self.parent_cloud.original_center_y

        # 初期位置を計算
        self.pos = pygame.math.Vector2(0, 0)
        self.update() # updateを呼んで正しい初期位置を設定

    def update(self):
        """
        親の雲の位置とスケールに合わせて自身の位置を更新する。
        """
        self.pos.x = self.parent_cloud.center.x
        self.pos.y = self.parent_cloud.center.y + (self.y_offset_from_center * self.parent_cloud.current_scale)

    def draw(self, screen):
        """
        ハートを画面に描画する。main.pyのdraw_heart関数をベースに作成。
        """
        points = []
        center_x, center_y = self.pos.x, self.pos.y

        for t_deg in range(0, 360):
            t_rad = math.radians(t_deg)
            scale = self.size / 32.0

            dx = 16 * (math.sin(t_rad) ** 3)
            dy = -(13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))

            x = center_x + dx * scale
            y = center_y + dy * scale
            points.append((x, y))

        pygame.draw.polygon(screen, self.color, points)
        if config.HEART_ITEM_OUTLINE_WIDTH > 0:
            pygame.draw.polygon(screen, config.BLACK, points, config.HEART_ITEM_OUTLINE_WIDTH)

    def collide_with_bird(self, bird):
        """
        弾(bird)と衝突したか判定する（単純な円形衝突判定）。
        :return: 衝突していればTrue、そうでなければFalse
        """
        distance = self.pos.distance_to(bird.pos)
        return distance < (self.size / 2 + bird.radius)
    