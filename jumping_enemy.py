import pygame
import random
import config
from enemy import Enemy

class JumpingEnemy(Enemy):
    """
    地面をジャンプしながら移動する、丸い敵を管理するクラス。
    基本的な機能はEnemyクラスを継承する。
    """
    def __init__(self, stat_multiplier):
        # 親クラスの初期化を呼び出す。これにより、基本的な属性(state, is_animatingなど)が設定される。
        # ただし、ステータスや位置は後で上書きする。
        super().__init__(stat_multiplier)

        # --- ジャンパー固有のステータスで上書き ---
        size = random.uniform(config.JUMPING_ENEMY_MIN_SIZE, config.JUMPING_ENEMY_MAX_SIZE)
        self.radius = size / 2
        self.original_width = size  # 親クラスとの互換性のため
        self.original_height = size

        # ステータス計算
        self.hp = size * config.JUMPING_ENEMY_HP_MULTIPLIER * stat_multiplier.get("hp", 1.0)
        self.max_hp = self.hp
        # ジャンプ時の横移動速度 (親クラスのspeedとは意味合いが異なるが、互換性のため設定)
        self.speed = (config.JUMPING_ENEMY_SPEED_BASE / size) * stat_multiplier.get("speed", 1.0)
        self.attack_power = size * config.JUMPING_ENEMY_ATTACK_MULTIPLIER * stat_multiplier.get("attack", 1.0)

        # --- 見た目の設定 ---
        self.color = config.JUMPING_ENEMY_COLOR
        self.draw_eyes = True # 目は描画する

        # --- 位置の再初期化 (親クラスと同じく、posは左上の座標とする) ---
        start_x = config.SCREEN_WIDTH - self.original_width + config.ENEMY_SPAWN_OFFSET_X
        start_y = config.GROUND_Y - self.original_height # 左上のY座標
        self.pos = pygame.math.Vector2(start_x, start_y)
        
        # Rectをposに合わせて再生成
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.original_width, self.original_height)

        # --- ジャンプ関連の属性 (ステップ3で利用) ---
        self.jump_state = "ON_GROUND" # "ON_GROUND", "JUMPING"
        self.jump_cooldown = random.uniform(
            config.JUMPING_ENEMY_JUMP_COOLDOWN_MIN,
            config.JUMPING_ENEMY_JUMP_COOLDOWN_MAX
        )
        self.last_jump_time = pygame.time.get_ticks()

    def update(self, tower, ground):
        """敵の状態を更新する。ジャンプ挙動を実装するために親クラスのupdateをオーバーライド。"""
        # --- 1. 状態に応じたアニメーション処理 (親クラスから流用) ---
        if self.state == "DYING":
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            progress = min(elapsed_time / config.ENEMY_DEATH_EFFECT_DURATION, 1.0)
            max_radius = (self.original_width / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER
            self.death_effect_radius = max_radius * progress
            return # 死亡中は以降の処理は不要

        if self.is_animating:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if elapsed_time >= config.ENEMY_ANIMATION_DURATION:
                self.is_animating = False
                self.current_scale = 1.0
            else:
                progress = elapsed_time / config.ENEMY_ANIMATION_DURATION
                self.current_scale = config.ENEMY_ANIMATION_MIN_SCALE + (1.0 - config.ENEMY_ANIMATION_MIN_SCALE) * progress
        
        center = self.rect.center
        self.rect.width = self.original_width * self.current_scale
        self.rect.height = self.original_height * self.current_scale
        self.rect.center = center

        # --- 2. AI: 行動決定 (ジャンプ) ---
        # ノックバック中でなく、地上にいる場合のみジャンプを試みる
        if self.velocity.length_squared() < 0.1 and self.jump_state == "ON_GROUND":
            current_time = pygame.time.get_ticks()
            if current_time - self.last_jump_time > self.jump_cooldown:
                self.jump_state = "JUMPING"
                jump_force_y = random.uniform(config.JUMPING_ENEMY_MIN_JUMP_FORCE, config.JUMPING_ENEMY_MAX_JUMP_FORCE)
                self.velocity.y = jump_force_y
                self.velocity.x = -self.speed # 左向きにジャンプ
                self.last_jump_time = current_time
                # 次のジャンプまでの待機時間を再設定
                self.jump_cooldown = random.uniform(
                    config.JUMPING_ENEMY_JUMP_COOLDOWN_MIN,
                    config.JUMPING_ENEMY_JUMP_COOLDOWN_MAX
                )

        # --- 3. 物理演算: 重力と移動 ---
        # 空中にいる場合（ジャンプ中またはノックバック中）は重力を適用
        if self.jump_state == "JUMPING" or self.velocity.length_squared() > 0.1:
            self.velocity.y += config.GRAVITY
            self.pos += self.velocity

            # ノックバック中の速度減衰（ジャンプの軌道には影響させない）
            if self.jump_state != "JUMPING":
                self.velocity *= config.ENEMY_FRICTION

            # 地面との衝突判定 (Y速度が正、つまり落下中の場合のみ)
            if self.rect.bottom >= ground.rect.top and self.velocity.y > 0:
                self.rect.bottom = ground.rect.top
                self.pos.y = self.rect.y # 浮動小数点座標も同期
                self.velocity.x = 0 # 地面に着いたら水平・垂直方向の速度をリセット
                self.velocity.y = 0
                self.jump_state = "ON_GROUND"

        # --- 4. 最終的な位置調整 ---
        # ノックバック中でなく、地上にいる場合は、地面のアニメーションに追従させる
        if self.jump_state == "ON_GROUND" and self.velocity.length_squared() < 0.1:
            self.rect.bottom = ground.rect.top
            self.pos.y = self.rect.y

        # 浮動小数点座標を整数のRectに反映
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def draw(self, screen):
        """敵（円形）を描画する。親クラスのdrawをオーバーライド。"""
        # --- パフォーマンス改善: 画面外のオブジェクトは描画しない ---
        # screen.get_rect()は毎回新しいRectオブジェクトを生成するため、
        # ループの外で一度だけ取得するのが理想的だが、クラス内ではここで取得するのが手軽。
        screen_rect = screen.get_rect()
        if not self.rect.colliderect(screen_rect):
            return

        if self.state == "ALIVE":
            # 現在のスケールを反映した半径と中心を計算
            current_radius = (self.rect.width / 2)
            center_pos = self.rect.center

            # 本体 (円)
            pygame.draw.circle(screen, self.color, center_pos, current_radius)
            # 枠線
            pygame.draw.circle(screen, config.BLACK, center_pos, current_radius, 2)

            # --- 目の描画処理 (Enemyクラスから流用し、円形に合わせる) ---
            if self.draw_eyes:
                # 1. 目の大きさを計算
                eye_radius = current_radius * config.JUMPING_ENEMY_EYE_SIZE_SCALE
                pupil_radius = eye_radius * config.ENEMY_EYE_PUPIL_SCALE

                # 2. 目の位置を計算
                offset_x = config.JUMPING_ENEMY_EYE_OFFSET_X_SCALE
                offset_y = config.JUMPING_ENEMY_EYE_OFFSET_Y_SCALE
                eye_center = (center_pos[0] + offset_x, center_pos[1] + offset_y)

                # 3. 描画
                pygame.draw.circle(screen, config.ENEMY_EYE_WHITE_COLOR, eye_center, eye_radius)
                pygame.draw.circle(screen, config.ENEMY_EYE_PUPIL_COLOR, eye_center, pupil_radius)
                pygame.draw.circle(screen, config.BLACK, eye_center, eye_radius, config.ENEMY_EYE_OUTLINE_WIDTH)

        elif self.state == "DYING":
            # 死亡エフェクトは親クラスのものをそのまま利用できるが、
            # 描画の基準点がself.rect.centerなので、ここで再実装する。
            progress = (pygame.time.get_ticks() - self.death_animation_start_time) / config.ENEMY_DEATH_EFFECT_DURATION
            progress = min(progress, 1.0)

            alpha = 255 * (1 - progress)
            max_radius = int((self.original_width / 2) * config.ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER)
            
            if max_radius <= 0: return

            surface_size = max_radius * 2
            effect_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            effect_color = (*config.ENEMY_DEATH_EFFECT_COLOR, alpha)
            
            current_radius = int(self.death_effect_radius)
            line_width = min(config.ENEMY_DEATH_EFFECT_LINE_WIDTH, current_radius)

            if line_width > 0:
                pygame.draw.circle(effect_surface, effect_color, (max_radius, max_radius), current_radius, line_width)

            # 親クラスと違い、死亡時の中心位置はself.rect.centerから取得
            top_left = self.rect.centerx - max_radius, self.rect.centery - max_radius
            screen.blit(effect_surface, top_left)

    # take_damage, destroy, knockback, is_finished は親クラスのものをそのまま使うので、
    # ここでオーバーライドする必要はない。