import pygame
import config
import math
import random
from enemy import Enemy
from weak_point import WeakPoint

class BossEnemy(Enemy):
    """
    巨大な地上ボスを管理するクラス。
    基本的な移動や描画はEnemyクラスを継承する。
    """
    def __init__(self, stat_multiplier):
        """
        ボス敵を初期化する。
        stat_multiplierは継承のために受け取るが、ボス固有の固定ステータスで上書きする。
        """
        # 親クラス(Enemy)の初期化を呼び出す。
        # これにより、アニメーションや状態管理などの基本機能がセットアップされる。
        super().__init__(stat_multiplier)
        self.draw_eyes = False # ボスは弱点が目なので、通常の目は描画しない

        # --- ボス固有のステータスで上書き ---
        boss_size = config.BOSS_SIZE
        self.original_width = boss_size
        self.original_height = boss_size

        # ステータスを固定値で設定
        self.max_hp = config.BOSS_MAX_HP
        self.hp = self.max_hp
        self.base_speed = config.BOSS_BASE_SPEED
        self.speed = self.base_speed
        self.attack_power = config.BOSS_ATTACK_POWER
        self.color = config.GREEN

        # --- 位置と見た目の再初期化 ---
        # サイズが変更されたので、rectを再計算する必要がある
        start_x = config.SCREEN_WIDTH - self.original_width + config.ENEMY_SPAWN_OFFSET_X
        start_y = config.GROUND_Y - self.original_height
        # 浮動小数点座標とRectの両方を、ボス固有のサイズと位置で再設定する
        self.pos = pygame.math.Vector2(start_x, start_y)
        self.rect = pygame.Rect(start_x, start_y, self.original_width, self.original_height)

        # --- 形態変化用の設定 ---
        self.persistent_scale = 1.0 # 永続的なスケール

        # 天使の輪のアニメーション用タイマー
        self.halo_animation_timer = 0

        # --- 弱点の設定 ---
        self.weak_points = []
        # ボスのサイズを基準に相対位置を決定
        half_size = self.original_width / 2
        # ボスの縁から、設定値分だけ内側に配置する
        offset = half_size - config.BOSS_WEAK_POINT_OFFSET
        
        # 弱点の位置を定義 (上、前、後)
        positions = [
            pygame.math.Vector2(0, -offset),      # Top
            pygame.math.Vector2(-offset, 0),     # Front (left)
            pygame.math.Vector2(offset, 0),      # Back (right)
        ]
        for pos in positions:
            self.weak_points.append(WeakPoint(self, pos))

        # 弱点切り替えタイマー
        self.weak_point_switch_interval = config.WEAK_POINT_SWITCH_INTERVAL
        self.weak_point_switch_timer = pygame.time.get_ticks()
        
        # 最初にランダムな弱点をアクティブにする
        if self.weak_points:
            random.choice(self.weak_points).is_active = True

        print("巨大なボスが生成された！")

    def update(self, tower, ground):
        # 親クラスのupdateを呼び出して、基本的な移動やひるみアニメーション(current_scaleの計算)を処理
        # この時点では、rectのサイズは一時的なひるみスケール(current_scale)のみで計算されている
        super().update(tower, ground)

        # 天使の輪のアニメーションタイマーを更新
        self.halo_animation_timer += config.BOSS_HALO_FLOAT_SPEED

        # スケールに基づいて速度を更新
        # (1.0 - スケール) は縮小した割合 (例: スケール0.8なら0.2)
        # これに倍率を掛けることで、速度の上昇カーブを調整する
        speed_increase_factor = (1.0 - self.persistent_scale) * config.BOSS_SPEED_SCALE_MULTIPLIER
        self.speed = self.base_speed * (1.0 + speed_increase_factor)

        # --- 永続スケールとひるみスケールを反映したサイズと位置の再計算 ---
        # 1. 新しい幅と高さを計算
        new_width = self.original_width * self.persistent_scale * self.current_scale
        new_height = self.original_height * self.persistent_scale * self.current_scale
        
        # 2. rectのサイズを更新
        self.rect.width = new_width
        self.rect.height = new_height
        
        # 3. rectの位置を調整。X座標はsuper()で更新されたものを維持し、Y座標はアニメーション中の地面に接地させる
        self.rect.bottom = ground.rect.top

        # 4. 浮動小数点座標(pos)のY成分のみ、地面に合わせたrectの位置を反映する。
        #    X成分はsuper()で計算された小数部分を維持するため、変更しない。
        self.pos.y = self.rect.y

        # 弱点の位置を更新
        for wp in self.weak_points:
            wp.update()

        # 弱点の切り替えロジック
        current_time = pygame.time.get_ticks()
        if current_time - self.weak_point_switch_timer > self.weak_point_switch_interval:
            print("時間経過により弱点の位置を変更します。")
            self._switch_weak_point()

    def _switch_weak_point(self):
        """弱点をランダムに切り替え、タイマーをリセットする。"""
        if len(self.weak_points) > 1:
            current_active_wp = next((wp for wp in self.weak_points if wp.is_active), None)
            candidates = [wp for wp in self.weak_points if wp != current_active_wp]
            if candidates:
                new_active_wp = random.choice(candidates)
                if current_active_wp:
                    current_active_wp.is_active = False
                new_active_wp.is_active = True
        # 切り替えタイマーを現在時刻でリセット
        self.weak_point_switch_timer = pygame.time.get_ticks()

    def force_switch_weak_point(self):
        """外部から弱点を強制的に切り替える。"""
        print("弱点ヒット！位置を即座に変更します。")
        self._switch_weak_point()

    def draw(self, screen):
        # 親クラスのdrawを呼び出して、ボス本体を描画
        super().draw(screen)

        # 生存中のみ天使の輪と弱点を描画
        if self.state == "ALIVE":
            # --- 天使の輪を描画 ---
            # 輪の幅と高さを計算 (ボスの現在のサイズに追従)
            halo_width = self.rect.width * config.BOSS_HALO_WIDTH_SCALE
            halo_height = self.rect.width * config.BOSS_HALO_HEIGHT_SCALE

            # 輪のY座標を計算 (上下にふわふわ動く)
            float_offset = math.sin(self.halo_animation_timer) * config.BOSS_HALO_FLOAT_AMPLITUDE
            
            # 輪の中心座標を計算
            halo_center_x = self.rect.centerx
            halo_center_y = self.rect.top + config.BOSS_HALO_OFFSET_Y + float_offset

            # 輪を描画するためのRectを作成
            halo_rect = pygame.Rect(0, 0, halo_width, halo_height)
            halo_rect.center = (halo_center_x, halo_center_y)

            # 楕円を描画
            pygame.draw.ellipse(screen, config.BOSS_HALO_COLOR, halo_rect, config.BOSS_HALO_LINE_WIDTH)

            # 弱点を描画
            for wp in self.weak_points:
                wp.draw(screen)

    def take_damage(self, amount):
        """
        ダメージ処理をオーバーライドし、縮小機能を追加する。
        """
        if self.state != "ALIVE":
            return False

        # 1. 永続スケールを縮小（最小値でクランプ）
        self.persistent_scale = max(
            self.persistent_scale - config.BOSS_SCALE_REDUCTION_ON_HIT,
            config.BOSS_MIN_SCALE
        )
        print(f"ボスが縮小！ 現在の永続スケール: {self.persistent_scale:.2f}")

        # 2. 親クラスのダメージ処理を呼び出す代わりに、ここで直接HPを減らす
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.destroy()
            return True
        return False
