import pygame
import config

class WeakPoint:
    """
    ボスに付属する「弱点」オブジェクト。
    位置、状態（アクティブ/非アクティブ）を管理し、自身の描画を行う。
    """
    def __init__(self, boss, relative_pos):
        """
        弱点を初期化する。
        :param boss: 親となるBossEnemyオブジェクト
        :param relative_pos: ボスの中心からの相対位置 (Vector2)
        """
        self.boss = boss
        self.relative_pos = relative_pos
        self.size = config.WEAK_POINT_SIZE
        self.radius = self.size / 2

        # 画面上の絶対座標。毎フレームupdateで更新される。
        self.absolute_pos = pygame.math.Vector2(0, 0)
        # 当たり判定用のRect。これも毎フレーム更新される。
        self.rect = pygame.Rect(0, 0, self.size, self.size)

        self.is_active = False # 初期状態は非アクティブ

    def update(self):
        """
        親であるボスの位置に基づいて、自身の絶対座標と当たり判定を更新する。
        """
        # ボスの中心座標をVector2として取得
        boss_center = pygame.math.Vector2(self.boss.rect.center)
        
        # ボスの現在の永続スケールを取得（なければ1.0）
        boss_scale = getattr(self.boss, 'persistent_scale', 1.0)

        # 絶対座標を計算
        self.absolute_pos = boss_center + (self.relative_pos * boss_scale)
        # Rectの中心を絶対座標に合わせる
        self.rect.center = self.absolute_pos

    def draw(self, screen):
        """弱点を画面に描画する。アクティブかどうかで色を変える。"""
        if self.is_active:
            # --- 開いた目（アクティブ）の描画 ---
            # 1. 白目を描画
            pygame.draw.circle(screen, config.WEAK_POINT_EYE_WHITE_COLOR, self.absolute_pos, self.radius)
            # 2. 黒目を描画
            pupil_radius = self.radius * config.WEAK_POINT_PUPIL_RADIUS_SCALE
            pygame.draw.circle(screen, config.WEAK_POINT_PUPIL_COLOR, self.absolute_pos, pupil_radius)
        else:
            # --- 閉じた目（非アクティブ）の描画 ---
            # 1. 背景を描画
            pygame.draw.circle(screen, config.WEAK_POINT_COLOR_INACTIVE, self.absolute_pos, self.radius)
            # 2. 閉じた瞼の線を描画
            start_pos = (self.absolute_pos.x - self.radius, self.absolute_pos.y)
            end_pos = (self.absolute_pos.x + self.radius, self.absolute_pos.y)
            pygame.draw.line(screen, config.BLACK, start_pos, end_pos, config.WEAK_POINT_CLOSED_LINE_WIDTH)

        # 輪郭線はどちらの状態でも最後に描画
        pygame.draw.circle(screen, config.BLACK, self.absolute_pos, self.radius, config.WEAK_POINT_OUTLINE_WIDTH)
