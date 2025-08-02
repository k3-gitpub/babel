import pygame
import random
import math
import config

class Particle:
    """
    画面に表示される小さな粒子（パーティクル）を管理するクラス。
    キラキラ光るエフェクトなどに使用する。
    """
    def __init__(self, x, y, lifetime, min_speed, max_speed, gravity, start_size, end_size, colors):
        self.pos = pygame.math.Vector2(x, y)
        
        # ランダムな方向に、ランダムな速度で飛び出すように設定
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(min_speed, max_speed)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
        
        # パーティクルの寿命と色、サイズを設定
        self.lifetime = lifetime
        self.max_lifetime = lifetime # 寿命の割合計算用に最大値も保持
        self.color = random.choice(colors)
        self.start_size = start_size
        self.end_size = end_size
        self.gravity = gravity

    def update(self):
        """パーティクルの位置と寿命を更新する。"""
        self.lifetime -= 1
        self.velocity.y += self.gravity # 重力を適用
        self.pos += self.velocity

    def draw(self, screen):
        """パーティクルを描画する。寿命に応じてサイズが変わる。"""
        if self.is_alive():
            life_ratio = self.lifetime / self.max_lifetime
            current_size = self.start_size * life_ratio + self.end_size * (1 - life_ratio)
            if current_size < 1:
                return

            # --- パフォーマンス改善: 画面外のパーティクルは描画しない ---
            particle_rect = pygame.Rect(self.pos.x - current_size, self.pos.y - current_size, current_size * 2, current_size * 2)
            if not screen.get_rect().colliderect(particle_rect):
                return

            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), int(current_size))

    def is_alive(self):
        """パーティクルがまだ表示時間内か判定する。"""
        return self.lifetime > 0