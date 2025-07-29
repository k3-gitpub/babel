# Copyright 2025 k3
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pygame
import math
import asyncio # Webアプリ(Pygbag)化のために追加
import random
import config
from bird import Bird
from cloud import Cloud
from ground import Ground
from enemy import Enemy
from tower import Tower
from heart_item import HeartItem
from flying_enemy import FlyingEnemy
from game_logic import GameLogicManager, calculate_trajectory
from ui import UIManager
from level_utils import create_cloud_layout
from scene_title import TitleScene

class Game:
    """ゲーム全体を管理するクラス"""
    def __init__(self):
        """ゲームの初期化"""
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Babel's Tower Shooter")
        self.clock = pygame.time.Clock()
        
        # フォントの準備
        ui_font = pygame.font.Font(None, 72)
        title_font = pygame.font.Font(None, 120)
        boss_font = pygame.font.Font(None, config.BOSS_NAME_FONT_SIZE)
        combo_font = pygame.font.Font(None, config.COMBO_TEXT_FONT_SIZE)

        # UIマネージャーのインスタンスを作成
        self.ui_manager = UIManager(self.screen, ui_font, title_font, boss_font, combo_font)

        # スリングショットのX座標と、タワーの初期の高さを定義
        self.slingshot_x = config.SLINGSHOT_X
        self.initial_tower_top_y = config.GROUND_Y - (config.TOWER_INITIAL_BLOCKS * config.TOWER_BLOCK_HEIGHT)

        # シーンのインスタンスを作成
        self.title_scene = TitleScene(self.ui_manager)

        # ゲームの状態をリセットして初期化
        self._reset_game()  # ゲームオブジェクトを先に初期化
        self.game_state = "TITLE"  # ゲームの初期状態を「タイトル」に設定

    def _setup_level(self, tower_top_y):
        """
        ゲームのレベル（弾、ブロック、雲）をセットアップし、オブジェクトをインスタンス変数として設定する。
        """
        tower_base_x = self.slingshot_x - config.TOWER_BLOCK_WIDTH / 2
        self.tower = Tower(tower_base_x, config.GROUND_Y, tower_top_y)
        self.bird = Bird(self.slingshot_x, self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y, config.BIRD_DEFAULT_RADIUS)
        self.clouds = create_cloud_layout(self.slingshot_x, tower_top_y)
        self.ground = Ground()
        self.enemies = []

    def _reset_game(self):
        """
        ゲームを初期化またはリセットし、すべてのオブジェクトとマネージャーをセットアップする。
        """
        self._setup_level(self.initial_tower_top_y)

        self.heart_items = []
        self.particles = []
        self.slingshot_pos = pygame.math.Vector2(self.slingshot_x, self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y)

        self.game_logic_manager = GameLogicManager(
            self.bird, self.tower, self.clouds, self.ground, self.enemies,
            self.heart_items, self.particles, self.slingshot_pos, self.ui_manager
        )

        # ゲームループに関わる状態もここでリセットする
        self.is_dragging = False
        self.trajectory_points = []
        self.mouse_pos = pygame.math.Vector2(0, 0)
        self.recall_button_rect = None
        self.running = True  # ゲームループの実行フラグ
        self.game_state = "PLAYING"  # ゲームをリセットしたら、状態を「プレイ中」にする

    def _handle_events(self):
        """イベント処理 (Input)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "TITLE":
                action = self.title_scene.process_event(event)
                if action == "START_GAME":
                    self._reset_game()

            elif self.game_state == "PLAYING":
                # キーボード入力
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self.game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"] or config.DEBUG:
                            self._reset_game()
                            print("--- Level Restarted ---")
                    
                    if config.DEBUG:
                        if pygame.K_1 <= event.key <= pygame.K_9:
                            stage_num = event.key - pygame.K_0
                            self.game_logic_manager.jump_to_stage(stage_num)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.recall_button_rect and self.recall_button_rect.collidepoint(event.pos):
                        self.bird.reset(self.slingshot_pos)
                        self.game_logic_manager.is_bird_callable = False
                        print("Bird recalled manually.")

                # マウス入力
                if not self.bird.is_flying and self.game_logic_manager.stage_state == "PLAYING":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and self.bird.is_clicked(event.pos):
                            self.is_dragging = True
                            self.mouse_pos.x, self.mouse_pos.y = event.pos
                    
                    if event.type == pygame.MOUSEMOTION:
                        if self.is_dragging:
                            self.mouse_pos.x, self.mouse_pos.y = event.pos

                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1 and self.is_dragging:
                            self.is_dragging = False
                            launch_vector = self.slingshot_pos - self.bird.pos
                            self.bird.launch(launch_vector)
                            self.trajectory_points.clear()

    def _update_state(self):
        """状態更新 (Update)"""
        # タイトル画面でも背景が動くように、雲は常に更新
        for cloud in self.clouds: cloud.update()

        if self.game_state == "TITLE":
            # タイトルシーンの状態を更新
            self.title_scene.update()
        elif self.game_state == "PLAYING":
            # プレイ中のみゲームオブジェクトの状態を更新
            self.slingshot_pos.y = self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y

            if self.is_dragging:
                self.bird.pos = self.mouse_pos.copy()
                distance = self.slingshot_pos.distance_to(self.bird.pos)
                if distance > config.MAX_PULL_DISTANCE:
                    if distance > 0:
                        direction = (self.bird.pos - self.slingshot_pos).normalize()
                        self.bird.pos = self.slingshot_pos + direction * config.MAX_PULL_DISTANCE
                    else:
                        self.bird.pos = self.slingshot_pos.copy()
            elif self.bird.is_flying:
                self.bird.update()
            else:
                self.bird.pos = self.slingshot_pos.copy()
                self.bird.start_pos = self.slingshot_pos.copy()

            for heart in self.heart_items: heart.update()
            for p in self.particles: p.update()
            for enemy in self.enemies:
                if isinstance(enemy, FlyingEnemy):
                    enemy.update(self.tower)
                else:
                    enemy.update(self.tower, self.ground)

            self.tower.update()
            self.ground.update()
            self.game_logic_manager.update()

            if self.is_dragging:
                current_launch_vector = self.slingshot_pos - self.bird.pos
                self.trajectory_points = calculate_trajectory(self.bird.pos, current_launch_vector)


    def _draw_screen(self):
        """描画処理 (Draw)"""
        # --- 共通の背景描画 ---
        self.screen.fill(config.BLUE)
        for cloud in self.clouds: cloud.draw(self.screen)
        self.ground.draw(self.screen)

        # --- 状態に応じた描画の切り替え ---
        if self.game_state == "TITLE":
            # タイトルシーンは、背景の上に自身のオブジェクト（タワー、ボール、UI）を描画する
            self.title_scene.draw(self.screen)

        elif self.game_state == "PLAYING":
            # ゲームプレイ中はカーソルを通常に戻す
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.tower.draw(self.screen)
            # --- ゲームプレイ中のオブジェクト描画 ---
            for enemy in self.enemies: enemy.draw(self.screen)
            for heart in self.heart_items: heart.draw(self.screen)
            for p in self.particles: p.draw(self.screen)

            if self.is_dragging:
                for point in self.trajectory_points:
                    pygame.draw.circle(self.screen, config.WHITE, (int(point.x), int(point.y)), config.TRAJECTORY_POINT_RADIUS)

            post_rect = pygame.Rect(
                self.slingshot_pos.x - config.SLINGSHOT_POST_WIDTH / 2,
                self.slingshot_pos.y,
                config.SLINGSHOT_POST_WIDTH,
                config.SLINGSHOT_POST_HEIGHT
            )
            pygame.draw.rect(self.screen, config.SLINGSHOT_POST_COLOR, post_rect)
            pygame.draw.rect(self.screen, config.BLACK, post_rect, 2)

            if self.is_dragging:
                pygame.draw.line(self.screen, config.BLACK, self.slingshot_pos, self.bird.pos, 5)
            
            if self.game_logic_manager.is_bird_callable:
                button_pos = self.slingshot_pos - pygame.math.Vector2(0, config.RECALL_BUTTON_OFFSET_Y)
                self.recall_button_rect = self.ui_manager.draw_recall_button(button_pos)
            else:
                self.recall_button_rect = None

            self.bird.draw(self.screen)

            # --- UIの描画 ---
            settings = self.game_logic_manager.stage_manager.get_current_stage_settings()
            enemies_to_clear = settings["clear_enemies_count"] if settings else 0
            boss = self.game_logic_manager.current_boss
            boss_name = settings.get("boss_name") if settings else None
            self.ui_manager.draw_game_hud(
                self.tower, 
                self.game_logic_manager.enemies_defeated_count,
                enemies_to_clear,
                self.game_logic_manager.stage_manager.current_stage,
                boss=boss,
                boss_name=boss_name
            )

            if self.game_logic_manager.stage_state != "PLAYING":
                self.ui_manager.draw_end_screen(self.game_logic_manager.stage_state)

            self.ui_manager.draw_ui_overlays()

    async def run(self):
        """ゲームのメインループ"""
        while self.running:
            self._handle_events()
            self._update_state()
            self._draw_screen()

            pygame.display.flip()
            await asyncio.sleep(0)
            self.clock.tick(config.FPS)

if __name__ == '__main__':
    game = Game()
    # Gameクラスの非同期メソッドrun()を実行
    asyncio.run(game.run())
