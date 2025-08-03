import pygame
import math
import config

# --- Birdクラス（弾） ---
class Bird:
    """弾（Bird）を管理するクラス"""
    def __init__(self, x, y, radius):
        self.start_pos = pygame.math.Vector2(x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.original_radius = radius # 元の半径を保持
        self.radius = radius # 現在の半径
        self.color = config.YELLOW  # 弾の色
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_flying = False
        self.launch_time = None # 発射された時間を記録
        self.last_power_up_time = 0 # 最後にパワーアップした時間
        self.low_velocity_start_time = None # 低速状態が始まった時間を記録
        self._update_stats() # 半径に基づいてステータスを初期化
        self.launched_upwards = False # 上方向に発射されたかどうかのフラグ
        self.combo_count = 0 # 1回のショットでのコンボ数を記録
        self.angle = 0 # 回転角度
        self.angular_velocity = 0 # 回転の角速度 (度/フレーム)
        self.radius_before_boost = 0 # 巨大化前の半径を保存
        self.size_boost_end_time = 0 # 巨大化効果の終了時間
        self._create_image() # 描画用のSurfaceを初期作成

    def _update_stats(self):
        """半径に基づいてHPと攻撃力を計算・更新する。"""
        # HPは小数点以下を考慮しないためintに変換
        self.max_hp = int(self.radius * config.BIRD_HP_MULTIPLIER)
        self.hp = self.max_hp
        self.attack_power = self.radius * config.BIRD_ATTACK_POWER_MULTIPLIER

    def _create_image(self):
        """
        現在の半径と状態に基づいて、ボールを描画したSurfaceを生成する。
        このSurfaceは回転や拡縮の元となる。
        """
        if self.radius <= 0: return

        surface_size = int(self.radius * 2 + 4)
        self.original_image = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        center = pygame.math.Vector2(surface_size / 2, surface_size / 2)

        # 本体を描画
        pygame.draw.circle(self.original_image, self.color, center, self.radius)
        pygame.draw.circle(self.original_image, config.BLACK, center, self.radius, 2)

        # --- 目の描画 (Surfaceのローカル座標系で) ---
        eye_radius = self.radius * config.BIRD_EYE_SIZE_SCALE
        pupil_radius = eye_radius * config.BIRD_PUPIL_SIZE_SCALE
        eye_offset_x = self.radius * config.BIRD_EYE_OFFSET_X_SCALE
        eye_offset_y = self.radius * config.BIRD_EYE_OFFSET_Y_SCALE
        eye_center_pos = center + pygame.math.Vector2(eye_offset_x, eye_offset_y)
        pupil_pos = eye_center_pos.copy()
        max_offset = (eye_radius - pupil_radius) * config.BIRD_PUPIL_MAX_OFFSET_SCALE
        direction = pygame.math.Vector2(1, 0) # アイドル時の向きで固定
        pupil_pos += direction * max_offset

        pygame.draw.circle(self.original_image, config.WHITE, eye_center_pos, eye_radius)
        pygame.draw.circle(self.original_image, config.BLACK, pupil_pos, pupil_radius)
        pygame.draw.circle(self.original_image, config.BLACK, eye_center_pos, eye_radius, config.BIRD_EYE_OUTLINE_WIDTH)

    def update(self, gravity=config.GRAVITY):
        """弾の位置を更新する（物理演算）"""
        if not self.is_flying:
            return

        self.velocity.y += gravity
        self.pos += self.velocity

        # --- 巨大化効果のチェック ---
        if self.size_boost_end_time > 0 and pygame.time.get_ticks() > self.size_boost_end_time:
            print("巨大化効果が終了。")
            self.radius = self.radius_before_boost
            self.size_boost_end_time = 0
            self._update_stats()
            self._create_image()

        # --- 回転処理 (角速度ベース) ---
        is_on_ground = self.pos.y + self.radius >= config.GROUND_Y - 1
        if is_on_ground and abs(self.velocity.x) > 0.1:
            # 地面にいるときは、滑らない回転をシミュレート
            # 角速度(deg/frame) = (v(px/frame) / r(px)) * (180 / PI)
            # 右に進む(vx > 0)と時計回り(角速度は負)になる
            self.angular_velocity = -math.degrees(self.velocity.x / self.radius)
        else:
            # 空中にいるときは、角速度を空気抵抗で減衰させる
            self.angular_velocity *= config.BIRD_ANGULAR_FRICTION

        # 計算された角速度を角度に適用
        self.angle = (self.angle + self.angular_velocity) % 360
    def draw(self, screen):
        """弾を描画する"""
        if not hasattr(self, 'original_image') or self.original_image is None:
            return

        rotated_image = pygame.transform.rotozoom(self.original_image, self.angle, 1.0)
        new_rect = rotated_image.get_rect(center=self.pos)
        screen.blit(rotated_image, new_rect)

    def launch(self, launch_vector):
        """弾を発射する"""
        self.is_flying = True
        self.velocity = launch_vector * config.LAUNCH_POWER_MULTIPLIER
        self.launch_time = pygame.time.get_ticks() # 発射時にタイマーを開始
        # 発射方向を記録（Y速度が負なら上向きに発射）
        self.launched_upwards = self.velocity.y < 0

    def apply_speed_boost(self):
        """スピードアップアイテムの効果を適用する。"""
        self.velocity *= config.SPEED_BOOST_MULTIPLIER
        print(f"スピードブースト！ 速度が {config.SPEED_BOOST_MULTIPLIER}倍に。")

    def apply_size_boost(self):
        """巨大化アイテムの効果を適用する。"""
        # すでに巨大化している場合は効果時間を延長するだけ
        if self.size_boost_end_time > 0:
            self.size_boost_end_time += config.SIZE_BOOST_DURATION
            print("巨大化効果を延長！")
        else:
            # 巨大化前の半径を保存
            self.radius_before_boost = self.radius
            # 半径を最大値まで大きくする
            self.radius = config.BIRD_MAX_RADIUS
            # ステータスを更新
            self._update_stats()
            self._create_image()
            print(f"巨大化！ 半径が {self.radius} に。")
        
        # 効果終了時間をセット
        self.size_boost_end_time = pygame.time.get_ticks() + config.SIZE_BOOST_DURATION

    def power_up(self):
        """ボールをパワーアップして大きくする。クールダウンを考慮する。"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_power_up_time > config.BIRD_POWER_UP_COOLDOWN:
            new_radius = self.radius * config.BIRD_POWER_UP_SCALE
            # 最大サイズを超えないように制限
            hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
            self.radius = min(new_radius, config.BIRD_MAX_RADIUS)
            # ステータスを更新（HPは割合を維持）
            self.max_hp = int(self.radius * config.BIRD_HP_MULTIPLIER)
            self.hp = int(self.max_hp * hp_ratio)
            self.attack_power = self.radius * config.BIRD_ATTACK_POWER_MULTIPLIER
            self.last_power_up_time = current_time # パワーアップした時間を更新
            self._create_image() # 画像を再生成
            print(f"パワーアップ！ボールの半径が {self.radius:.1f} になった！") # デバッグ用

    def increment_combo(self):
        """コンボ数を1増やし、現在のコンボ数を返す。"""
        self.combo_count += 1
        return self.combo_count

    def take_damage(self, amount):
        """ダメージを受けてHPを減らす。HPが0以下になったらTrueを返す。"""
        self.hp -= amount
        print(f"バードが {amount:.1f} のダメージを受けた！残りHP: {self.hp}/{self.max_hp}")
        if self.hp <= 0:
            return True # HPが0以下になったことを通知
        return False

    def bounce_off_cloud(self, collided_puff_info):
        """
        雲に当たってバウンドする処理。
        めり込みの解消と、不必要な連続衝突の防止も行う。
        """
        cloud_puff_center, cloud_puff_radius = collided_puff_info

        # 衝突点での法線ベクトルを計算（雲の円の中心 -> 弾の中心）
        # normalize()で長さを1の単位ベクトルにする
        normal = (self.pos - cloud_puff_center).normalize()

        # --- 衝突方向のチェック ---
        # 速度ベクトルと法線ベクトルの内積を計算し、オブジェクトが離れようとしている場合は処理しない
        # (内積 > 0 は、速度ベクトルと法線ベクトルが同じような方向を向いている = 離れている)
        if self.velocity.dot(normal) > 0:
            return

        # --- 回転の追加 ---
        # 速度ベクトルの法線に垂直な成分（接線ベクトル）を計算
        tangent = pygame.math.Vector2(-normal.y, normal.x)
        # 接線方向の速度
        tangential_speed = self.velocity.dot(tangent)
        # 接線速度に応じて角速度を変化させる（時計回りが負の回転）
        self.angular_velocity -= tangential_speed * config.BIRD_COLLISION_SPIN_FACTOR

        # --- 位置の補正（めり込み解消） ---
        # めり込み量を計算し、法線方向に押し出すことでめり込みを解消する
        distance = self.pos.distance_to(cloud_puff_center)
        overlap = (self.radius + cloud_puff_radius) - distance
        self.pos += normal * overlap

        # --- 速度の反射 ---
        reflected_velocity = self.velocity.reflect(normal)
        self.velocity = reflected_velocity * config.CLOUD_BOUNCINESS

    def collide_and_bounce_off_rect(self, rect_obj, bounciness):
        """
        四角形のオブジェクトと衝突判定を行い、衝突していればバウンドさせる。
        :param rect_obj: rect属性を持つオブジェクト (Block, Enemyなど)
        :param bounciness: 反発係数
        :return: 衝突していればTrue、そうでなければFalse
        """
        # ステップ1: 円の中心から最も近い四角形上の点を見つける
        closest_x = max(rect_obj.rect.left, min(self.pos.x, rect_obj.rect.right))
        closest_y = max(rect_obj.rect.top, min(self.pos.y, rect_obj.rect.bottom))
        closest_point = pygame.math.Vector2(closest_x, closest_y)

        # ステップ2: その点と円の中心との距離を計算し、衝突を判定
        distance = self.pos.distance_to(closest_point)
        if distance >= self.radius:
            return False # 衝突していない

        # ステップ3: 衝突法線ベクトルを計算
        if distance > 0.01:
            normal = (self.pos - closest_point).normalize()
        else: # めり込んでいる場合
            normal = (self.pos - pygame.math.Vector2(rect_obj.rect.center)).normalize()

        # ステップ4: 衝突方向のチェック（不要な連続衝突を防ぐ）
        if self.velocity.dot(normal) > 0:
            return False # すでに離れようとしている

        # --- 回転の追加 ---
        # 衝突時の接線速度からスピンを計算して角速度に加える
        tangent = pygame.math.Vector2(-normal.y, normal.x)
        tangential_speed = self.velocity.dot(tangent)
        # 時計回りが負の回転になるように符号を調整
        self.angular_velocity -= tangential_speed * config.BIRD_COLLISION_SPIN_FACTOR

        # ステップ5: 位置の補正（めり込み解消）
        overlap = self.radius - distance
        self.pos += normal * overlap

        # ステップ6: 速度の反射
        reflected_velocity = self.velocity.reflect(normal)
        self.velocity = reflected_velocity * bounciness

        return True

    def is_clicked(self, mouse_pos):
        """マウスカーソルが弾の上にあるか判定する"""
        return self.pos.distance_to(mouse_pos) < self.radius
    
    def update_for_title_screen(self, slingshot_pos):
        """
        タイトル画面専用の更新処理。ボールが画面外に出ることを許可し、
        画面下に大きく外れた場合や、動きが止まった場合にリセットする。
        """
        if not self.is_flying:
            return

        # 既存のupdateを呼び出して重力などを適用
        self.update()

        # リセット条件: 画面下に大きく外れた、または速度がほぼゼロになった
        if self.pos.y > config.SCREEN_HEIGHT + self.radius * 5 or \
           self.velocity.length_squared() < config.BIRD_RESET_MIN_VELOCITY_SQUARED:
            self.reset(slingshot_pos)

    def reset(self, new_start_pos=None):
        """
        弾を初期位置に戻す。
        新しい開始位置が指定された場合、それを新しい基準位置として更新する。
        """
        if new_start_pos:
            self.start_pos = new_start_pos.copy()

        self.pos = self.start_pos.copy()
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_flying = False
        self.radius = self.original_radius # 半径を元に戻す
        self._update_stats() # HPと攻撃力をリセット
        self.launch_time = None # リセット時にタイマーをリセット
        self.last_power_up_time = 0 # パワーアップのクールタイムもリセット
        self.launched_upwards = False # 発射方向フラグをリセット
        self.combo_count = 0 # コンボカウントをリセット
        self.size_boost_end_time = 0 # 巨大化効果もリセット
        self.angle = 0 # 角度をリセット
        self.angular_velocity = 0 # 角速度をリセット
        self._create_image() # 画像を再生成

    def cancel_launch(self):
        """
        発射をキャンセルし、ボールをスリングショットの位置に戻す。
        resetと似ているが、HPや半径は変更しない。
        """
        self.pos = self.start_pos.copy()
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_flying = False
        self.angle = 0
        self.angular_velocity = 0
