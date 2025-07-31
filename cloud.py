import pygame
import random
import math
import config

class Cloud:
    """
    複数の円を組み合わせて雲を表現し、描画するクラス。
    """
    def __init__(self, center_x, center_y, num_puffs):
        """
        雲を初期化する。
        :param center_x: 雲の中心のX座標
        :param center_y: 雲の中心のY座標
        :param num_puffs: 雲を構成する円の数
        """
        self.center = pygame.math.Vector2(center_x, center_y)
        self.original_center_y = center_y # 浮遊アニメーションの基準となるY座標
        self.original_puffs = [] # スケール変更前の円の情報を保持するリスト

        for _ in range(num_puffs):
            # 雲の中心からのランダムなオフセットを決定
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-20, 20)

            # 円の半径をランダムに決定
            radius = random.randint(25, 40)

            # 中心からの相対位置ベクトルと半径を保存
            offset_vector = pygame.math.Vector2(offset_x, offset_y)
            self.original_puffs.append((offset_vector, radius))

        # アニメーション関連の属性
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale = 1.0
        
        # 浮遊アニメーション用のタイマー。各インスタンスで異なる動きになるよう、開始値をランダムにする
        self.float_animation_timer = random.uniform(0, 2 * math.pi)

        # 描画と当たり判定に使うpuffsリストを初期化
        self.puffs = []
        self._update_puffs_for_drawing()

    def _update_puffs_for_drawing(self):
        """現在のスケールに基づいて、描画/当たり判定用のpuffsリストを再計算する。"""
        self.puffs.clear()
        for offset, radius in self.original_puffs:
            # スケールを適用
            scaled_offset = offset * self.current_scale
            scaled_radius = radius * self.current_scale

            # 絶対座標を計算
            puff_center = self.center + scaled_offset

            self.puffs.append(((puff_center.x, puff_center.y), scaled_radius))

    def update(self):
        """雲のアニメーション状態（浮遊、衝突）を更新する。"""
        # --- 1. 浮遊アニメーション (常に実行) ---
        self.float_animation_timer += config.CLOUD_FLOAT_SPEED
        float_offset = math.sin(self.float_animation_timer) * config.CLOUD_FLOAT_AMPLITUDE
        self.center.y = self.original_center_y + float_offset

        # --- 2. 衝突アニメーション (is_animatingがTrueの時のみ) ---
        if self.is_animating:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time

            if elapsed_time >= config.CLOUD_ANIMATION_DURATION:
                self.is_animating = False
                self.current_scale = 1.0
            else:
                progress = elapsed_time / config.CLOUD_ANIMATION_DURATION
                self.current_scale = config.CLOUD_ANIMATION_MIN_SCALE + (1.0 - config.CLOUD_ANIMATION_MIN_SCALE) * progress

        # --- 3. 最終的な描画用puffsを更新 (常に実行) ---
        # 浮遊による位置変更と、衝突によるスケール変更を両方反映する
        self._update_puffs_for_drawing()

    def start_animation(self):
        """衝突アニメーションを開始する。"""
        if not self.is_animating: # アニメーション中に再度トリガーされるのを防ぐ
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def draw(self, screen):
        """
        雲を画面に描画する。
        """
        for puff_center, puff_radius in self.puffs:
            pygame.draw.circle(screen, config.WHITE, puff_center, puff_radius)

    def collide_with_bird(self, bird):
        """
        弾(bird)が雲のいずれかの部分に衝突しているか判定する。
        衝突している場合は、衝突した円の中心座標と半径のタプルを返す。
        :param bird: Birdオブジェクト
        :return: 衝突していれば(中心座標(Vector2), 半径(float))、そうでなければNone
        """
        bird_pos = bird.pos
        for puff_center_tuple, puff_radius in self.puffs:
            puff_pos = pygame.math.Vector2(puff_center_tuple)
            # アニメーションで半径が変わるため、当たり判定も動的に
            if bird_pos.distance_to(puff_pos) < bird.radius + puff_radius:
                return (puff_pos, puff_radius) # 中心座標と半径を返す
        return None # どの円にも当たらなければNoneを返す
