import pygame
import config

class Ground:
    """地面を管理するクラス。衝突時のアニメーションも含む。"""
    def __init__(self):
        """地面を初期化する。"""
        # 地面の位置と大きさを保持
        self.original_rect = pygame.Rect(0, config.GROUND_Y, config.SCREEN_WIDTH, config.SCREEN_HEIGHT - config.GROUND_Y)
        self.rect = self.original_rect.copy()
        self.color = config.GREEN

        # アニメーション関連の属性
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale_y = 1.0 # Y方向のスケールのみ変更

    def start_animation(self):
        """衝突アニメーションを開始する。"""
        if not self.is_animating:
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def update(self):
        """地面のアニメーション状態を更新する。"""
        if not self.is_animating:
            return

        elapsed_time = pygame.time.get_ticks() - self.animation_start_time

        if elapsed_time >= config.GROUND_ANIMATION_DURATION:
            self.is_animating = False
            self.current_scale_y = 1.0
        else:
            progress = elapsed_time / config.GROUND_ANIMATION_DURATION
            min_scale = config.GROUND_ANIMATION_MIN_SCALE
            self.current_scale_y = min_scale + (1.0 - min_scale) * progress

        self.rect.height = self.original_rect.height * self.current_scale_y
        self.rect.bottom = self.original_rect.bottom # 地面の下辺を画面最下部に固定

    def draw(self, screen):
        """地面を描画する。"""
        pygame.draw.rect(screen, self.color, self.rect)