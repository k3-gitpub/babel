import pygame
import config

class Block:
    """塔を構成する四角いブロックを管理するクラス。HPと物理挙動を持つ。"""
    def __init__(self, x, y, width, height):
        # スケール変更前の元の形状と位置を保持
        self.original_rect = pygame.Rect(x, y, width, height) # 落下停止時の基準位置
        # 描画と当たり判定に使うRectオブジェクト
        self.rect = self.original_rect.copy()
        self.color = config.WHITE

        # --- ステータスと状態 ---
        self.hp = config.BLOCK_HP
        self.max_hp = config.BLOCK_HP
        self.state = "ALIVE"  # "ALIVE", "DYING", "DESTROYED"

        # --- 物理演算関連 ---
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_falling = False

        # --- アニメーション関連 ---
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale = 1.0

        # --- 死亡エフェクト用 ---
        self.death_animation_start_time = 0
        self.death_effect_radius = 0
        self.center_on_death = (0, 0)

    def start_animation(self):
        """衝突アニメーションを開始する。"""
        if not self.is_animating and self.state == "ALIVE":
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def update(self, blocks_below, ground_y):
        """ブロックの状態を更新する。落下やアニメーションを処理する。"""
        if self.state == "ALIVE":
            # --- 落下処理 ---
            if self.is_falling:
                self.velocity.y += config.GRAVITY
                self.rect.y += self.velocity.y

                # 地面との衝突判定
                if self.rect.bottom >= ground_y:
                    self.rect.bottom = ground_y
                    self.stop_falling()
                else:
                    # 他のブロックとの衝突判定
                    for other_block in blocks_below:
                        # 落下中でない安定したブロックの上にのみ着地
                        if not other_block.is_falling and self.rect.colliderect(other_block.rect):
                            # ブロックの底が、他のブロックの上半分より下にある場合に着地
                            if self.rect.bottom > other_block.rect.centery:
                                self.rect.bottom = other_block.rect.top
                                self.stop_falling()
                                break # 一つのブロックに着地したらループを抜ける

            # --- 衝突アニメーション処理 ---
            if self.is_animating:
                elapsed_time = pygame.time.get_ticks() - self.animation_start_time
                if elapsed_time >= config.TOWER_ANIMATION_DURATION:
                    self.is_animating = False
                    self.current_scale = 1.0
                else:
                    progress = elapsed_time / config.TOWER_ANIMATION_DURATION
                    self.current_scale = config.TOWER_ANIMATION_MIN_SCALE + (1.0 - config.TOWER_ANIMATION_MIN_SCALE) * progress
                
                # 現在のスケールをRectに反映（中心を基準に拡縮）
                center = self.rect.center
                self.rect.width = self.original_rect.width * self.current_scale
                self.rect.height = self.original_rect.height * self.current_scale
                self.rect.center = center

        elif self.state == "DYING":
            # 死亡エフェクトのアニメーション
            elapsed_time = pygame.time.get_ticks() - self.death_animation_start_time
            if elapsed_time >= config.BLOCK_DEATH_EFFECT_DURATION:
                self.state = "DESTROYED" # アニメーション完了
            else:
                progress = elapsed_time / config.BLOCK_DEATH_EFFECT_DURATION
                max_radius = (self.original_rect.width / 2) * config.BLOCK_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER
                self.death_effect_radius = max_radius * progress

    def draw(self, screen):
        """ブロックを描画する"""
        if self.state == "ALIVE":
            # ブロック本体を描画
            pygame.draw.rect(screen, self.color, self.rect)
            # 見やすくするために黒い枠線を描画
            pygame.draw.rect(screen, config.BLACK, self.rect, 2)

            # --- 窓の描画処理を追加 ---
            # 窓のサイズを計算 (ブロックの現在のサイズに追従)
            window_width = self.rect.width * config.BLOCK_WINDOW_WIDTH_RATIO
            window_height = self.rect.height * config.BLOCK_WINDOW_HEIGHT_RATIO
            
            # 窓のRectを作成 (ブロックの中心に配置)
            window_rect = pygame.Rect(0, 0, window_width, window_height)
            window_rect.center = self.rect.center

            # 窓と枠線を描画
            pygame.draw.rect(screen, config.BLOCK_WINDOW_COLOR, window_rect)
            pygame.draw.rect(screen, config.BLACK, window_rect, config.BLOCK_WINDOW_OUTLINE_WIDTH)
        elif self.state == "DYING":
            # 死亡エフェクト（広がる半透明の円）を描画
            progress = (pygame.time.get_ticks() - self.death_animation_start_time) / config.BLOCK_DEATH_EFFECT_DURATION
            progress = min(progress, 1.0)

            alpha = 255 * (1 - progress)
            max_radius = int(self.death_effect_radius * 2)
            if max_radius <= 0: return

            effect_surface = pygame.Surface((max_radius, max_radius), pygame.SRCALPHA)
            effect_color = (*config.BLOCK_DEATH_EFFECT_COLOR, alpha)
            
            current_radius = int(self.death_effect_radius)
            line_width = min(config.BLOCK_DEATH_EFFECT_LINE_WIDTH, current_radius)
            if line_width > 0:
                pygame.draw.circle(effect_surface, effect_color, (current_radius, current_radius), current_radius, line_width)

            top_left = self.center_on_death[0] - current_radius, self.center_on_death[1] - current_radius
            screen.blit(effect_surface, top_left)

    def take_damage(self, amount):
        """ダメージを受けてHPを減らす。HPが0以下になったらTrueを返す。"""
        if self.state != "ALIVE":
            return False
        
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.destroy()
            return True # 破壊された
        return False # まだ生きている

    def destroy(self):
        """ブロックを破壊し、死亡アニメーションを開始する。"""
        if self.state == "ALIVE":
            self.state = "DYING"
            self.death_animation_start_time = pygame.time.get_ticks()
            self.center_on_death = self.rect.center

    def start_falling(self):
        """ブロックの落下を開始する。"""
        if not self.is_falling and self.state == "ALIVE":
            self.is_falling = True
            # 落下開始時の基準位置を保存
            self.original_rect.topleft = self.rect.topleft

    def stop_falling(self):
        """ブロックの落下を停止する。"""
        self.is_falling = False
        self.velocity.y = 0
        # 落下停止時の位置を新しい基準位置として保存
        self.original_rect.topleft = self.rect.topleft

    def is_finished(self):
        """ブロックが完全に消滅したか（リストから削除してよいか）を返す。"""
        return self.state == "DESTROYED"