import pygame
import math
import config
import random

class BaseItem:
    """
    全てのアイテムの共通機能を持つ基底クラス。
    - 雲への追従、または空中での浮遊
    - バードとの衝突判定
    """
    def __init__(self, parent_cloud=None, position=None, size=40):
        """
        アイテムを初期化する。
        :param parent_cloud: このアイテムが乗る親のCloudオブジェクト (指定した場合)
        :param position: 空中に直接出現させる場合の位置 (Vector2)
        :param size: アイテムの当たり判定や描画の基準となるサイズ
        """
        self.parent_cloud = parent_cloud
        self.size = size
        self.pos = pygame.math.Vector2(0, 0)

        # 出現アニメーション用の状態
        self.state = "SPAWNING" # "SPAWNING", "IDLE"
        self.spawn_start_time = pygame.time.get_ticks()
        self.current_scale = 0.0 # 0.0 (見えない) から 1.0 (通常サイズ) へ

        if self.parent_cloud:
            # --- 親の雲の「元の形」を基準に、相対的なYオフセットを計算 ---
            original_top_y = self.parent_cloud.original_center_y
            if self.parent_cloud.original_puffs:
                original_top_y = min(
                    self.parent_cloud.original_center_y + offset.y - radius 
                    for offset, radius in self.parent_cloud.original_puffs
                )
            self.y_offset_from_center = (original_top_y + config.ITEM_Y_OFFSET) - self.parent_cloud.original_center_y
        else:
            # 空中出現の場合、浮遊アニメーションの基準位置とタイマーを設定
            self.base_pos = position.copy()
            self.pos = self.base_pos.copy()
            self.float_timer = random.uniform(0, 2 * math.pi)

    def update(self):
        """アイテムの状態を更新する。"""
        if self.state == "SPAWNING":
            elapsed_time = pygame.time.get_ticks() - self.spawn_start_time
            if elapsed_time >= config.ITEM_SPAWN_ANIMATION_DURATION:
                self.current_scale = 1.0
                self.state = "IDLE"
            else:
                # 一気に大きくなってから元に戻るアニメーション
                duration = config.ITEM_SPAWN_ANIMATION_DURATION
                half_duration = duration / 2.0
                max_scale = config.ITEM_SPAWN_ANIMATION_MAX_SCALE

                if elapsed_time < half_duration:
                    # 前半: 0から最大スケールへ線形に増加
                    progress = elapsed_time / half_duration
                    self.current_scale = progress * max_scale
                else:
                    # 後半: 最大スケールから通常スケール(1.0)へ線形に減少
                    progress = (elapsed_time - half_duration) / half_duration
                    self.current_scale = max_scale - (progress * (max_scale - 1.0))

        # 常に位置の更新は行う
        if self.parent_cloud:
            self.pos.x = self.parent_cloud.center.x
            self.pos.y = self.parent_cloud.center.y + (self.y_offset_from_center * self.parent_cloud.current_scale)
        elif self.state == "IDLE": # 空中浮遊は出現アニメーション完了後
            self.float_timer += config.CLOUD_FLOAT_SPEED
            float_offset = math.sin(self.float_timer) * config.CLOUD_FLOAT_AMPLITUDE
            self.pos.y = self.base_pos.y + float_offset

    def collide_with_bird(self, bird):
        """弾(bird)と衝突したか判定する（単純な円形衝突判定）。"""
        # 出現アニメーション中は衝突しない
        if self.state != "IDLE":
            return False
        distance = self.pos.distance_to(bird.pos)
        return distance < (self.size * self.current_scale / 2 + bird.radius)