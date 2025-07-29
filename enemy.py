import pygame
import random
import config

class Enemy:
    """地上を歩く敵を管理するクラス"""
    def __init__(self, stat_multiplier):
        # --- 大きさとステータスの決定 ---
        # ランダムなサイズを決定（正方形とする）
        size = random.uniform(config.ENEMY_MIN_SIZE, config.ENEMY_MAX_SIZE)
        self.original_width = size  # アニメーション用に元のサイズを保持
        self.original_height = size

        # 大きさとステージ補正に基づいてステータスを計算
        self.hp = size * config.ENEMY_HP_MULTIPLIER * stat_multiplier.get("hp", 1.0)
        self.max_hp = self.hp # HPバー表示用に最大HPも保持
        # 大きいほど遅くなるが、最低速度は下回らないようにする
        base_speed = config.ENEMY_SPEED_BASE / size
        self.speed = max(base_speed, config.ENEMY_MIN_SPEED) * stat_multiplier.get("speed", 1.0)
        self.attack_power = size * config.ENEMY_ATTACK_MULTIPLIER * stat_multiplier.get("attack", 1.0)

        # --- 位置と見た目の初期化 ---
        # 画面の右側、地面の上に配置
        start_x = config.SCREEN_WIDTH - self.original_width + config.ENEMY_SPAWN_OFFSET_X
        start_y = config.GROUND_Y - self.original_height
        # 浮動小数点数で座標を管理するためのVector2
        self.pos = pygame.math.Vector2(start_x, start_y)
        # 描画と当たり判定用のRect
        self.rect = pygame.Rect(round(self.pos.x), round(self.pos.y), self.original_width, self.original_height)
        self.color = config.RED
        self.draw_eyes = True # 目を描画するかのフラグ

        # ノックバック用の速度ベクトル
        self.velocity = pygame.math.Vector2(0, 0)

        # アニメーション関連の属性
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale = 1.0

        # 状態管理 ("ALIVE", "DYING")
        self.state = "ALIVE"
        # 死亡エフェクト用の属性
        self.death_animation_start_time = 0
        self.death_effect_radius = 0

    def start_animation(self):
        """衝突アニメーションを開始する。"""
        if not self.is_animating and self.state == "ALIVE":
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def update(self, tower, ground):
        """敵の位置を更新する。ノックバックと通常移動、地面の動きへの追従を管理する。"""
        # --- 状態に応じた更新処理 ---
        if self.state == "ALIVE":
            # 衝突アニメーション処理
            if self.is_animating:
                elapsed_time = pygame.time.get_ticks() - self.animation_start_time
                if elapsed_time >= config.ENEMY_ANIMATION_DURATION:
                    self.is_animating = False
                    self.current_scale = 1.0
                else:
                    progress = elapsed_time / config.ENEMY_ANIMATION_DURATION
                    self.current_scale = config.ENEMY_ANIMATION_MIN_SCALE + (1.0 - config.ENEMY_ANIMATION_MIN_SCALE) * progress
            
            # 現在のスケールをRectに反映
            center = self.rect.center
            self.rect.width = self.original_width * self.current_scale
            self.rect.height = self.original_height * self.current_scale
            self.rect.center = center

        elif self.state == "DYING":
            # 死亡エフェクトのアニメーション
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            progress = min(elapsed_time / config.ENEMY_DEATH_EFFECT_DURATION, 1.0)
            max_radius = (self.original_width / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER
            self.death_effect_radius = max_radius * progress

        # --- 共通の物理演算処理 (生存中も死亡中も適用) ---
        # length_squared()は平方根を計算しないため、length()より高速
        if self.velocity.length_squared() > 0.1:
            self.velocity.y += config.GRAVITY # 重力を適用
            self.pos += self.velocity # 浮動小数点座標を更新
            self.velocity *= config.ENEMY_FRICTION # 減速

            # 地面との衝突判定
            if self.rect.bottom > ground.rect.top:
                self.rect.bottom = ground.rect.top
                self.pos.y = self.rect.y # Rectの位置をposに反映
                self.velocity.y *= -config.ENEMY_GROUND_BOUNCINESS # Y方向の速度を反転・減衰（バウンド）
                self.velocity.x *= config.ENEMY_GROUND_FRICTION    # X方向の速度を摩擦で減衰（滑り）

                if abs(self.velocity.y) < 1:
                    self.velocity.y = 0
        elif self.state == "ALIVE":
            # ノックバックの速度がほぼ無くなったら、通常の移動に戻る
            self.velocity.x = 0
            self.velocity.y = 0
            self.pos.x -= self.speed # 浮動小数点座標を更新

        # 最後に、浮動小数点座標を整数のRectに反映させる
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # 地面がアニメーションで動いた場合に追従させる
        # ノックバック中でない場合、常に地面に接地させる
        if self.velocity.length_squared() <= 0.1 and self.state == "ALIVE":
            self.rect.bottom = ground.rect.top
            self.pos.y = self.rect.y

    def draw(self, screen):
        """敵を描画する"""
        if self.state == "ALIVE":
            # 本体
            pygame.draw.rect(screen, self.color, self.rect)
            # 枠線
            pygame.draw.rect(screen, config.BLACK, self.rect, 2)

            # --- 目の描画処理 ---
            if self.draw_eyes:
                # 1. 目の大きさを計算
                eye_radius = self.rect.width * config.GROUND_ENEMY_EYE_SIZE_SCALE
                pupil_radius = eye_radius * config.ENEMY_EYE_PUPIL_SCALE

                # 2. 目の位置を計算
                offset_x = self.rect.width * config.GROUND_ENEMY_EYE_OFFSET_X_SCALE
                offset_y = self.rect.height * config.GROUND_ENEMY_EYE_OFFSET_Y_SCALE
                eye_center = (self.rect.centerx + offset_x, self.rect.centery + offset_y)

                # 3. 描画
                pygame.draw.circle(screen, config.ENEMY_EYE_WHITE_COLOR, eye_center, eye_radius)
                pygame.draw.circle(screen, config.ENEMY_EYE_PUPIL_COLOR, eye_center, pupil_radius)
                pygame.draw.circle(screen, config.BLACK, eye_center, eye_radius, config.ENEMY_EYE_OUTLINE_WIDTH)

        elif self.state == "DYING":
            # 死亡エフェクト（広がる半透明の円）を描画
            progress = (pygame.time.get_ticks() - self.death_animation_start_time) / config.ENEMY_DEATH_EFFECT_DURATION
            progress = min(progress, 1.0) # 1.0を超えないようにする

            # 徐々に透明にする (alpha: 255 -> 0)
            alpha = 255 * (1 - progress)

            # 円を描画するための新しいSurfaceを作成
            max_radius = int((self.original_width / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER)
            surface_size = max_radius * 2
            effect_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)

            # 色にアルファ値を適用
            effect_color = (*config.ENEMY_DEATH_EFFECT_COLOR, alpha)

            # 線の太さが半径を超えないように調整（太すぎると描画が崩れるため）
            current_radius = int(self.death_effect_radius)
            line_width = min(config.ENEMY_DEATH_EFFECT_LINE_WIDTH, current_radius)

            # Surfaceの中心に、現在の半径で円を描く
            pygame.draw.circle(effect_surface, effect_color, (max_radius, max_radius), current_radius, line_width)

            # Surfaceを画面の正しい位置に描画
            top_left = self.rect.centerx - max_radius, self.rect.centery - max_radius
            screen.blit(effect_surface, top_left)

    def take_damage(self, amount):
        """ダメージを受けてHPを減らす。HPが0以下になったらTrueを返す。"""
        if self.state != "ALIVE":
            return False # すでに死亡中の場合は何もしない

        self.hp -= amount
        print(f"敵が {amount:.1f} のダメージを受けた！残りHP: {self.hp:.1f}/{self.max_hp:.1f}")
        if self.hp <= 0:
            self.hp = 0
            self.destroy()
            print("敵がHPを失い、死亡状態に移行！")
            return True # HPが0以下になったことを通知
        return False

    def destroy(self):
        """外部から敵を破壊し、死亡アニメーションを開始する。"""
        if self.state != "DYING":
            self.state = "DYING"
            self.death_animation_start_time = pygame.time.get_ticks()

    def knockback(self, direction, force):
        """指定された方向に力を加えてノックバックさせる"""
        self.velocity += direction * force

    def is_finished(self):
        """死亡アニメーションが完了したか判定する"""
        if self.state == "DYING":
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            return elapsed_time >= config.ENEMY_DEATH_EFFECT_DURATION
        return False