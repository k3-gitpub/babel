import pygame
import random
import math
import config

class FlyingEnemy:
    """空中を飛行する三角の敵を管理するクラス"""

    def __init__(self, x, y, stat_multiplier):
        """
        飛行する敵を初期化する。
        :param x: 出現位置のX座標
        :param y: 出現位置のY座標
        :param stat_multiplier: ステータス補正値の辞書
        """
        # --- 大きさとステータスの決定 ---
        size = random.uniform(config.FLYING_ENEMY_MIN_SIZE, config.FLYING_ENEMY_MAX_SIZE)
        self.size = size
        self.original_size = size # アニメーション用

        # 大きさとステージ補正に基づいてステータスを計算
        self.hp = self.size * config.FLYING_ENEMY_HP_MULTIPLIER * stat_multiplier.get("hp", 1.0)
        self.max_hp = self.hp
        base_speed = config.FLYING_ENEMY_SPEED_BASE / self.size
        self.speed = max(base_speed, config.FLYING_ENEMY_MIN_SPEED) * stat_multiplier.get("speed", 1.0)
        self.attack_power = self.size * config.FLYING_ENEMY_ATTACK_MULTIPLIER * stat_multiplier.get("attack", 1.0)

        # --- 位置と見た目の初期化 ---
        self.pos = pygame.math.Vector2(x, y)
        self.color = config.FLYING_ENEMY_COLOR
        self.angle = 180 # 左向き (度)

        # ノックバック用の速度ベクトル
        self.velocity = pygame.math.Vector2(0, 0)

        # アニメーション関連
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale = 1.0

        # 状態管理 ("PATROLING", "ATTACKING", "DYING")
        self.state = "PATROLING"
        # 攻撃モードで狙うY座標のオフセット
        self.target_y_offset = 0
        # 攻撃を開始する、タワーからのX軸距離
        self.trigger_distance = random.uniform(
            config.FLYING_ENEMY_ATTACK_RANGE_MIN,
            config.FLYING_ENEMY_ATTACK_RANGE_MAX
        )
        # 死亡エフェクト用
        self.death_animation_start_time = 0
        self.death_effect_radius = 0

        # --- 画像サーフェスの作成 ---
        # 描画の安定性を高めるため、一度画像(Surface)に三角形を描画し、
        # それを回転・拡縮して画面にblitする方式に変更します。
        # これにより、画面外の頂点を扱う際のPygameの描画アーティファクトを回避できます。
        size_int = int(self.original_size)
        self.original_image = pygame.Surface((size_int, size_int), pygame.SRCALPHA)

        # --- 本体（三角形）を描画 ---
        # ポイントは (先端, 左下, 左上)
        points = [
            (size_int, size_int / 2), 
            (0, 0), 
            (0, size_int)
        ]
        pygame.draw.polygon(self.original_image, self.color, points)
        pygame.draw.polygon(self.original_image, config.BLACK, points, config.FLYING_ENEMY_OUTLINE_WIDTH)

        # --- 目をoriginal_imageに描き込む ---
        eye_center = (size_int / 2, size_int / 2 + 2)
        eye_radius = self.original_size * config.FLYING_ENEMY_EYE_SIZE_SCALE
        pupil_radius = eye_radius * config.ENEMY_EYE_PUPIL_SCALE

        pygame.draw.circle(self.original_image, config.ENEMY_EYE_WHITE_COLOR, eye_center, eye_radius)
        pygame.draw.circle(self.original_image, config.ENEMY_EYE_PUPIL_COLOR, eye_center, pupil_radius)
        pygame.draw.circle(self.original_image, config.BLACK, eye_center, eye_radius, config.ENEMY_EYE_OUTLINE_WIDTH)

        self.image = self.original_image.copy()
        
        # 当たり判定用のRectを計算
        self._update_rect()

    def start_animation(self):
        """衝突アニメーションを開始する。"""
        # 生存中かつ、別のアニメーションが実行中でない場合のみ
        if self.state != "DYING" and not self.is_animating:
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def _update_rect(self):
        """現在の位置とサイズから当たり判定用のRectを計算する。"""
        # 三角形を包含する最小の四角形を計算
        # 簡単のため、中心に正方形のRectを割り当てる
        self.rect = pygame.Rect(
            self.pos.x - self.size / 2,
            self.pos.y - self.size / 2,
            self.size,
            self.size
        )

    def update(self, tower):
        """敵の位置や状態を更新する。"""
        if self.state == "DYING":
            # 死亡エフェクトのアニメーション
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            progress = min(elapsed_time / config.ENEMY_DEATH_EFFECT_DURATION, 1.0)
            max_radius = (self.original_size / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER
            self.death_effect_radius = max_radius * progress
            # 死亡中は以降の処理は不要
            return

        # --- 生存中の処理 (PATROLING or ATTACKING) ---

        # 1. 衝突アニメーション処理
        if self.is_animating:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if elapsed_time >= config.ENEMY_ANIMATION_DURATION:
                self.is_animating = False
                self.current_scale = 1.0
            else:
                progress = elapsed_time / config.ENEMY_ANIMATION_DURATION
                # 最小スケールから通常スケールに徐々に戻る
                self.current_scale = config.ENEMY_ANIMATION_MIN_SCALE + (1.0 - config.ENEMY_ANIMATION_MIN_SCALE) * progress
        
        # 2. 現在のスケールをsizeに反映
        self.size = self.original_size * self.current_scale

        # 3. 状態ごとの移動ロジック
        if self.state == "PATROLING":
            # 左にまっすぐ進む
            self.pos.x -= self.speed
            
            # タワーが破壊されていない場合のみ攻撃ロジックを実行
            if not tower.is_destroyed():
                # タワーの中心X座標を計算
                tower_center_x = tower.base_x + config.TOWER_BLOCK_WIDTH / 2
                
                # 自身のX座標が、個別に設定された攻撃開始距離に入ったか判定
                # 敵は左に進んでいるので、X座標が「タワーの中心X + トリガー距離」以下になったら攻撃開始
                if self.pos.x <= tower_center_x + self.trigger_distance:
                    self.state = "ATTACKING"
                    # 攻撃モードに移行する際に、ターゲットとするY座標のオフセットをランダムに決定
                    self.target_y_offset = random.uniform(
                        config.FLYING_ENEMY_TARGET_Y_MIN,
                        config.FLYING_ENEMY_TARGET_Y_MAX
                    )
                    print(f"飛行する敵が攻撃モードに移行！ トリガー距離: {self.trigger_distance:.1f}")

        elif self.state == "ATTACKING":
            # タワーが破壊されたら、そのまま直進する
            if tower.is_destroyed():
                # 現在の角度のまま直進
                move_rad = math.radians(self.angle)
                # PygameのY軸は下向きなので、sinの符号を反転させる
                move_direction = pygame.math.Vector2(math.cos(move_rad), -math.sin(move_rad))
                self.pos += move_direction * self.speed
            else:
                # --- 目標への滑らかな追尾 ---
                # 1. ターゲットへの方向ベクトルと目標角度を計算
                target_x = tower.base_x + config.TOWER_BLOCK_WIDTH / 2
                # インスタンスごとに保持しているランダムなオフセットを使用してターゲットY座標を計算
                target_y = tower.get_top_y() + config.TOWER_BLOCK_HEIGHT / 2 + self.target_y_offset
                target_pos = pygame.math.Vector2(target_x, target_y)
                direction_to_target = target_pos - self.pos                
                
                if direction_to_target.length_squared() > 0:
                    target_angle = math.degrees(math.atan2(-direction_to_target.y, direction_to_target.x))
                    
                    # 2. 現在の角度と目標角度の差を計算 (-180から180の範囲に正規化)
                    angle_diff = (target_angle - self.angle + 180) % 360 - 180
                    
                    # 3. 角度を滑らかに変化させる
                    # 差が回転速度より小さい場合は、直接目標角度に設定
                    if abs(angle_diff) < config.FLYING_ENEMY_ROTATION_SPEED:
                        self.angle = target_angle
                    else:
                        # 差が大きい場合は、回転速度分だけ角度を変化させる
                        self.angle += math.copysign(config.FLYING_ENEMY_ROTATION_SPEED, angle_diff)

                # 4. 現在の角度の方向に移動
                move_rad = math.radians(self.angle)
                # PygameのY軸は下向きなので、sinの符号を反転させる
                move_direction = pygame.math.Vector2(math.cos(move_rad), -math.sin(move_rad))
                self.pos += move_direction * self.speed

        # 4. ノックバック処理 (空中なので重力は適用しない)
        if self.velocity.length_squared() > 0.1:
            self.pos += self.velocity
            self.velocity *= config.ENEMY_FRICTION # 空中抵抗

        # 5. 毎フレームRectを更新
        self._update_rect()

    def draw(self, screen):
        """敵（三角形）を描画する。"""
        if self.state == "DYING":
            # 死亡エフェクトの描画 (Enemyクラスとほぼ同じロジック)
            progress = (pygame.time.get_ticks() - self.death_animation_start_time) / config.ENEMY_DEATH_EFFECT_DURATION
            progress = min(progress, 1.0)
            alpha = 255 * (1 - progress)
            max_radius = int((self.original_size / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER)

            # 描画する円がなければ何もしない
            if max_radius <= 0:
                return

            surface_size = max_radius * 2
            effect_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            effect_color = (*config.ENEMY_DEATH_EFFECT_COLOR, alpha)
            current_radius = int(self.death_effect_radius)
            line_width = min(config.ENEMY_DEATH_EFFECT_LINE_WIDTH, current_radius)

            if line_width > 0:
                pygame.draw.circle(effect_surface, effect_color, (max_radius, max_radius), current_radius, line_width)

            top_left = self.pos.x - max_radius, self.pos.y - max_radius
            screen.blit(effect_surface, top_left)
            return

        # --- 生存中の描画 ---
        # 1. マスターイメージを現在の角度とスケールで回転・拡縮する
        #    pygame.transform.rotozoomは高品質な回転と拡縮を同時に行います。
        #    self.angleは数学的な角度（反時計回り）であり、rotozoomも反時計回りに回転するため、
        #    角度をそのまま渡すことで、移動方向と画像の向きが一致します。
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, self.current_scale)
        
        # 2. 回転・拡縮後の画像のRectを取得し、中心を敵の現在位置に合わせる
        rotated_rect = self.image.get_rect(center=self.pos)
        # 3. 計算された位置に画像をblit（転送）する
        screen.blit(self.image, rotated_rect)

    def take_damage(self, amount):
        if self.state == "DYING": return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.destroy()
            return True
        return False

    def destroy(self):
        if self.state != "DYING":
            self.state = "DYING"
            self.death_animation_start_time = pygame.time.get_ticks()

    def knockback(self, direction, force):
        self.velocity += direction * force

    def is_finished(self):
        if self.state == "DYING":
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            return elapsed_time >= config.ENEMY_DEATH_EFFECT_DURATION
        return False