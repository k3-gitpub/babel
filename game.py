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
from speed_up_item import SpeedUpItem
from size_up_item import SizeUpItem
from flying_enemy import FlyingEnemy
from game_logic import GameLogicManager, calculate_trajectory
from ui import UIManager
from level_utils import create_cloud_layout
from scene_title import TitleScene
from audio_manager import AudioManager
from data_manager import DataManager

class Game:
    """ゲーム全体を管理するクラス"""
    def __init__(self, start_stage=None):
        """ゲームの初期化。開始ステージを指定できる。"""
        pygame.init()
        # mixerの初期化。Webアプリ化で失敗することがあるため、try-exceptで囲む
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")
            self.mixer_initialized = True
        except pygame.error as e:
            print(f"警告: Pygame mixerの初期化に失敗しました: {e}")
            self.mixer_initialized = False

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Babel's Tower Shooter")
        self.clock = pygame.time.Clock()
        
        # フォントの準備
        ui_font = pygame.font.Font(None, 72)
        title_font = pygame.font.Font(None, 120)
        boss_font = pygame.font.Font(None, config.BOSS_NAME_FONT_SIZE)
        combo_font = pygame.font.Font(None, config.COMBO_TEXT_FONT_SIZE)
        result_font = pygame.font.Font(None, 40)

        # UIマネージャーのインスタンスを作成
        self.ui_manager = UIManager(self.screen, ui_font, title_font, boss_font, combo_font, result_font)

        # データマネージャーのインスタンスを作成し、ハイスコアを読み込む
        self.data_manager = DataManager()
        save_data = self.data_manager.load_data()
        self.high_score = save_data.get("high_score", 0)
        self.best_combo = save_data.get("best_combo", 0)
        self.best_tower_height = save_data.get("best_tower_height", 0)
        sound_enabled = save_data.get("sound_enabled", True)

        # オーディオマネージャーのインスタンスを作成
        if self.mixer_initialized:
            self.audio_manager = AudioManager(initial_enabled=sound_enabled)
        else:
            self.audio_manager = None

        # スリングショットのX座標と、タワーの初期の高さを定義
        self.slingshot_x = config.SLINGSHOT_X
        self.initial_tower_top_y = config.GROUND_Y - (config.TOWER_INITIAL_BLOCKS * config.TOWER_BLOCK_HEIGHT)

        # シーンのインスタンスを作成
        self.title_scene = TitleScene(self.ui_manager, self.audio_manager)

        # ゲームの状態をリセットして初期化
        self._reset_game(play_start_sound=False)

        # 開始ステージが指定されていれば、直接そのステージから開始する
        if start_stage is not None and config.DEBUG:
            print(f"デバッグモード: ステージ {start_stage} から直接開始します。")
            self.game_logic_manager.jump_to_stage(start_stage)
            self.game_state = "PLAYING"
        else:
            # 通常はタイトル画面から開始
            self.game_state = "TITLE"

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

    def _reset_game(self, play_start_sound=True):
        """
        ゲームを初期化またはリセットし、すべてのオブジェクトとマネージャーをセットアップする。
        """
        self._setup_level(self.initial_tower_top_y)

        self.heart_items = []
        self.speed_up_items = []
        self.size_up_items = []
        self.particles = []
        self.slingshot_pos = pygame.math.Vector2(self.slingshot_x, self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y)

        self.game_logic_manager = GameLogicManager(
            self.bird, self.tower, self.clouds, self.ground, self.enemies,
            self.heart_items, self.speed_up_items, self.size_up_items,
            self.particles, self.slingshot_pos, self.ui_manager, self.audio_manager,
            play_start_sound=play_start_sound
        )

        # ゲームループに関わる状態もここでリセットする
        self.is_dragging = False
        self.drag_start_pos = None # ドラッグ開始位置を記録
        self.is_game_over_processed = False # ゲームオーバー処理が完了したかのフラグ
        self.is_release_pending = False # リリース待機中フラグ
        self.release_pending_start_time = 0 # リリース待機開始時間
        self.pending_launch_vector = None # 発射待機中のベクトル
        self.trajectory_points = []
        self.mouse_pos = pygame.math.Vector2(0, 0)
        self.recall_button_rect = None
        self.running = True  # ゲームループの実行フラグ
        # DRAG表示関連
        self.show_drag_indicator = True
        self.last_activity_time = pygame.time.get_ticks()
        self.was_bird_flying = False
        if self.audio_manager:
            self.audio_manager.reset_scale()

    def _handle_events(self):
        """イベント処理 (Input)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "TITLE":
                action = self.title_scene.process_event(event)
                if action == "START_GAME":
                    self._reset_game(play_start_sound=True)
                    self.game_state = "PLAYING"
                elif action == "TOGGLE_SOUND":
                    # サウンド設定が変更されたら、現在の設定を保存する
                    self._save_current_settings()


            elif self.game_state == "PLAYING":
                # キーボード入力
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self.game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"] or config.DEBUG:
                            self._reset_game(play_start_sound=True)
                            self.game_state = "PLAYING"
                            print("--- Level Restarted ---")
                    
                    if config.DEBUG:
                        if pygame.K_1 <= event.key <= pygame.K_9:
                            stage_num = event.key - pygame.K_0
                            self.game_logic_manager.jump_to_stage(stage_num)
                        if event.key == pygame.K_c:
                            print("--- Clearing save data (High Score & Best Combo) ---")
                            self.high_score = 0
                            self.best_combo = 0
                            self.best_tower_height = 0
                            self._save_current_settings()
                
                # ゲームオーバー/クリア時のボタン入力
                if self.game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"]:
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.FINGERDOWN:
                        pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (event.x * config.SCREEN_WIDTH, event.y * config.SCREEN_HEIGHT)
                        # リスタートボタンがクリックされたか判定
                        if self.ui_manager.end_screen.restart_button_rect.collidepoint(pos):
                            if self.audio_manager: self.audio_manager.play_ui_click_sound()
                            self._reset_game(play_start_sound=True)
                            self.game_state = "PLAYING"
                            print("--- Level Restarted via Button ---")
                
                # --- マウス・タッチ入力の統合 ---
                
                # 1. プレスダウン処理
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.FINGERDOWN:
                    pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (event.x * config.SCREEN_WIDTH, event.y * config.SCREEN_HEIGHT)
                    
                    # リコールボタンの判定
                    if self.recall_button_rect and self.recall_button_rect.collidepoint(pos):
                        if self.audio_manager: self.audio_manager.reset_scale()
                        self.bird.reset(self.slingshot_pos)
                        self.game_logic_manager.is_bird_callable = False
                        self.last_activity_time = pygame.time.get_ticks()
                        print("Bird recalled manually.")
                    # リリース待機中に再度プレスされたら、ドラッグを再開
                    elif self.is_release_pending:
                        self.is_release_pending = False
                        self.is_dragging = True
                        print("Release cancelled, resuming drag.")
                    # 画面のどこかをタッチしてドラッグ開始
                    elif not self.bird.is_flying and self.game_logic_manager.stage_state == "PLAYING":
                        # is_clicked の条件を削除し、UI以外の場所ならドラッグ開始
                        self.is_dragging = True
                        self.drag_start_pos = pygame.math.Vector2(pos) # タッチ開始点を記録
                        self.mouse_pos.x, self.mouse_pos.y = pos # 現在のタッチ位置も更新
                        self.last_activity_time = pygame.time.get_ticks()

                # 2. ドラッグ中の移動処理
                if self.is_dragging and (event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION):
                    pos = event.pos if event.type == pygame.MOUSEMOTION else (event.x * config.SCREEN_WIDTH, event.y * config.SCREEN_HEIGHT)
                    self.mouse_pos.x, self.mouse_pos.y = pos

                # 3. リリース処理
                if self.is_dragging and ((event.type == pygame.MOUSEBUTTONUP and event.button == 1) or event.type == pygame.FINGERUP):
                    self.is_dragging = False
                    self.is_release_pending = True
                    self.release_pending_start_time = pygame.time.get_ticks()
                    # 発射待機中のベクトルを保存
                    self.pending_launch_vector = self.slingshot_pos - self.bird.pos
                    print("Release pending...")

    def _update_state(self):
        """状態更新 (Update)"""
        current_time = pygame.time.get_ticks()

        # タイトル画面でも背景が動くように、雲は常に更新
        for cloud in self.clouds: cloud.update()

        # オーディオマネージャーの更新
        if self.audio_manager:
            is_boss_stage = False
            # PLAYING状態の時のみステージ設定を確認
            if self.game_state == "PLAYING":
                settings = self.game_logic_manager.stage_manager.get_current_stage_settings()
                if settings:
                    is_boss_stage = settings.get("is_boss_stage", False)
            
            self.audio_manager.update(self.game_state, is_boss_stage)

        if self.game_state == "TITLE":
            # タイトルシーンの状態を更新
            self.title_scene.update()
        elif self.game_state == "PLAYING":
            # --- DRAG表示のロジック ---
            # UI要素のアニメーションを更新
            self.ui_manager.update()

            # ボールがちょうどリセットされた瞬間を検知
            if self.was_bird_flying and not self.bird.is_flying:
                self.last_activity_time = current_time
            self.was_bird_flying = self.bird.is_flying

            # 入力待機状態で一定時間経過したら、DRAG表示を再度有効にする
            if not self.is_dragging and not self.is_release_pending and not self.bird.is_flying and self.game_logic_manager.stage_state == "PLAYING":
                if current_time - self.last_activity_time > config.DRAG_PROMPT_DELAY:
                    self.show_drag_indicator = True
            else:
                self.show_drag_indicator = False

            # --- リリース待機処理 ---
            if self.is_release_pending and current_time - self.release_pending_start_time > config.DRAG_RELEASE_DELAY:
                self.is_release_pending = False
                pull_distance = self.pending_launch_vector.length()
                if pull_distance > config.MIN_PULL_DISTANCE_TO_LAUNCH:
                    print("Launch confirmed.")
                    self.bird.launch(self.pending_launch_vector)
                    self.last_activity_time = pygame.time.get_ticks()
                else:
                    print("Pull distance too short, launch cancelled.")
                    self.bird.cancel_launch()
                self.pending_launch_vector = None
                self.trajectory_points.clear()

            # プレイ中のみゲームオブジェクトの状態を更新
            self.slingshot_pos.y = self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y

            if self.is_dragging or self.is_release_pending:
                # ドラッグ開始点からのベクトルを計算
                drag_vector = self.mouse_pos - self.drag_start_pos
                # スリングショットの位置に、ドラッグベクトルを加算してボールを配置（直感的な引っ張り操作）
                self.bird.pos = self.slingshot_pos + drag_vector

                distance = self.slingshot_pos.distance_to(self.bird.pos)
                if distance > config.MAX_PULL_DISTANCE:
                    if distance > 0:
                        direction = (self.bird.pos - self.slingshot_pos).normalize()
                        self.bird.pos = self.slingshot_pos + direction * config.MAX_PULL_DISTANCE
            elif self.bird.is_flying:
                self.bird.update(gravity=config.GRAVITY)
            else:
                self.bird.pos = self.slingshot_pos.copy()
                self.bird.start_pos = self.slingshot_pos.copy()

            for heart in self.heart_items: heart.update()
            for item in self.speed_up_items: item.update()
            for item in self.size_up_items: item.update()
            for p in self.particles: p.update()
            for enemy in self.enemies:
                if isinstance(enemy, FlyingEnemy):
                    enemy.update(self.tower)
                else:
                    enemy.update(self.tower, self.ground)

            self.tower.update()
            self.ground.update()
            self.game_logic_manager.update()

            if self.is_dragging or self.is_release_pending:
                current_launch_vector = self.slingshot_pos - self.bird.pos
                self.trajectory_points = calculate_trajectory(self.bird.pos, current_launch_vector)

            # --- ゲームオーバー/クリア時のスコア記録処理 ---
            if self.game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"] and not self.is_game_over_processed:
                self._process_game_over_scores()

    def _process_game_over_scores(self):
        """ゲームオーバー/クリア時にスコアを処理し、ハイスコアを更新・保存する。"""
        print("ゲーム終了処理を開始します。")

        # ゲームクリア時のみタワーボーナスを加算
        if self.game_logic_manager.stage_state == "GAME_WON":
            self.game_logic_manager.calculate_and_add_tower_bonus()

        current_score = self.game_logic_manager.current_score
        max_combo = self.game_logic_manager.max_combo_count
        final_height = self.game_logic_manager.final_block_count
        
        record_updated = False
        if current_score > self.high_score:
            print(f"ハイスコア更新！ {self.high_score} -> {current_score}")
            self.high_score = current_score
            record_updated = True
        
        if max_combo > self.best_combo:
            print(f"ベストコンボ更新！ {self.best_combo} -> {max_combo}")
            self.best_combo = max_combo
            record_updated = True

        # ゲームクリア時のみ、最高の高さをチェック・更新
        if self.game_logic_manager.stage_state == "GAME_WON" and final_height > self.best_tower_height:
            print(f"最高のタワーの高さ更新！ {self.best_tower_height} -> {final_height}")
            self.best_tower_height = final_height
            record_updated = True

        if record_updated:
            save_data = {
                "high_score": self.high_score,
                "best_combo": self.best_combo,
                "best_tower_height": self.best_tower_height
            }
            self.data_manager.save_data(save_data)
        
        self.is_game_over_processed = True

    def _save_current_settings(self):
        """現在の設定（ハイスコア、サウンドON/OFFなど）をファイルに保存する。"""
        if not self.data_manager:
            return
        
        sound_enabled = self.audio_manager.enabled if self.audio_manager else True
        save_data = {
            "high_score": self.high_score,
            "best_combo": self.best_combo,
            "sound_enabled": sound_enabled,
            "best_tower_height": self.best_tower_height
        }
        self.data_manager.save_data(save_data)

    def _draw_screen(self):
        """描画処理 (Draw)"""
        mouse_pos = pygame.mouse.get_pos()
        # --- 共通の背景描画 ---
        self.screen.fill(config.BLUE)
        for cloud in self.clouds: cloud.draw(self.screen)
        self.ground.draw(self.screen)

        # --- 状態に応じた描画の切り替え ---
        if self.game_state == "TITLE":
            # タイトルシーンは、背景の上に自身のオブジェクト（タワー、ボール、UI）を描画する
            self.title_scene.draw(self.screen)

        elif self.game_state == "PLAYING":
            # --- カーソル形状の更新 ---
            if self.game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"]:
                is_restart_hovered = self.ui_manager.end_screen.restart_button_rect.collidepoint(mouse_pos)
                if is_restart_hovered:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.tower.draw(self.screen)
            # --- ゲームプレイ中のオブジェクト描画 ---
            for enemy in self.enemies: enemy.draw(self.screen)
            for heart in self.heart_items: heart.draw(self.screen)
            for item in self.speed_up_items: item.draw(self.screen)
            for item in self.size_up_items: item.draw(self.screen)
            for p in self.particles: p.draw(self.screen)

            if self.is_dragging or self.is_release_pending:
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

            if self.is_dragging or self.is_release_pending:
                pygame.draw.line(self.screen, config.BLACK, self.slingshot_pos, self.bird.pos, 5)
            
            # --- DRAG表示 (点滅) ---
            if self.show_drag_indicator:
                drag_text_pos = (self.bird.pos.x, self.bird.pos.y - self.bird.radius - 40)
                self.ui_manager.draw_blinking_text(
                    "DRAG",
                    drag_text_pos,
                    config.BLACK,
                    2
                )

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
                self.game_logic_manager.max_combo_count,
                self.game_logic_manager.current_score,
                self.game_logic_manager.combo_gauge,
                config.COMBO_GAUGE_MAX,
                boss=boss,
                boss_name=boss_name
            )

            if self.game_logic_manager.stage_state != "PLAYING":
                self.ui_manager.draw_end_screen(
                    self.game_logic_manager.stage_state,
                    score=self.game_logic_manager.current_score,
                    high_score=self.high_score,
                    max_combo=self.game_logic_manager.max_combo_count,
                    best_combo=self.best_combo,
                    tower_height=self.game_logic_manager.final_block_count,
                    tower_bonus=self.game_logic_manager.tower_bonus_score,
                    best_tower_height=self.best_tower_height,
                    mouse_pos=mouse_pos
                )

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

        # ゲームループを抜けたらmixerを終了
        if self.mixer_initialized:
            pygame.mixer.quit()
