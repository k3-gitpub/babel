import pygame
import config
from bird import Bird
from tower import Tower
from game_logic import calculate_trajectory
from ui_utils import draw_text
import random
from enemy import Enemy
from ground import Ground

class TitleScene:
    """
    インタラクティブなタイトル画面を管理するクラス。
    プレイヤーはここで基本操作を試すことができる。
    """
    def __init__(self, ui_manager, audio_manager):
        """
        TitleSceneを初期化する。
        :param ui_manager: UI描画に使用するUIManagerのインスタンス
        :param audio_manager: 音声再生に使用するAudioManagerのインスタンス
        """
        self.ui_manager = ui_manager
        self.audio_manager = audio_manager
        self.title_font = pygame.font.Font(None, 90) # タイトル用に少し小さめのフォント
        self.license_font = pygame.font.Font(None, 24) # ライセンス表示用のフォント
        self.info_font = pygame.font.Font(None, 36) # 操作説明用のフォント
        self.start_button_font = pygame.font.Font(None, 48) # スタートボタン専用のフォント
        self.sound_button_font = pygame.font.Font(None, 32) # サウンドボタン用のフォント

        # タイトルシーン専用の地面と敵を生成
        self.ground = Ground()

        # --- シーン専用のオブジェクトを作成 ---
        # tower_x = config.SCREEN_WIDTH / 2 - config.TOWER_BLOCK_WIDTH / 2
        tower_x = 180 # タワーの左端のX座標
        tower_top_y = config.GROUND_Y - (config.TITLE_TOWER_BLOCKS * config.TOWER_BLOCK_HEIGHT) # ブロックの高さ
        self.tower = Tower(tower_x, config.GROUND_Y, tower_top_y)
        
        self.slingshot_pos = pygame.math.Vector2(
            tower_x + config.TOWER_BLOCK_WIDTH / 2,
            self.tower.get_top_y() + config.SLINGSHOT_OFFSET_Y
        )
        self.bird = Bird(self.slingshot_pos.x, self.slingshot_pos.y, config.BIRD_DEFAULT_RADIUS)
        self.bird.pos = self.slingshot_pos.copy() # 初期位置を確定

        # --- 状態変数を追加 ---
        self.is_dragging = False
        self.trajectory_points = []
        self.mouse_pos = pygame.math.Vector2(0, 0)
        self.show_drag_indicator = True # DRAG表示用のフラグ
        self.last_activity_time = pygame.time.get_ticks() # 最後の入力やボールリセットの時間
        self.drag_start_pos = None # ドラッグ開始位置を記録
        self.was_bird_flying = False # 前フレームでボールが飛んでいたか

        # にぎやかし用の敵を管理するリストとタイマー
        self.decorative_enemies = []
        self.spawn_count = 0 # スポーンした敵の数を記録
        self.spawn_offsets = [150, 250, 100, 200] # 画面右端からのオフセットリスト

        # 最初の敵を即座に出現させ、タイマーを開始する
        self._spawn_decorative_enemy()
        self.last_enemy_spawn_time = pygame.time.get_ticks()

        # スタートボタンのRectを定義
        button_width, button_height = 200, 60

        # スタートボタンの位置
        button_x = config.SCREEN_WIDTH / 2 - button_width / 2
        button_y = config.SCREEN_HEIGHT * 3 / 4 - 100 # 画面下部に配置
        self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # サウンドボタンのRectを定義 (横長のボタンに変更)
        sound_button_width, sound_button_height = 180, 40
        self.sound_button_rect = pygame.Rect(
            config.SCREEN_WIDTH - sound_button_width - 20, # 右端から20px
            20, # 上端から20px
            sound_button_width,
            sound_button_height
        )

    def _spawn_decorative_enemy(self):
        """利用可能な位置に、にぎやかし用の敵を一体生成する。"""
        # オフセットリストを順番に使い、X座標を決定
        # これにより、敵は画面右端から一定の距離で繰り返し出現する
        offset = self.spawn_offsets[self.spawn_count % len(self.spawn_offsets)]
        x_pos = config.SCREEN_WIDTH - offset

        size = random.randint(config.ENEMY_MIN_SIZE, config.ENEMY_MAX_SIZE - 20)
        enemy_settings = {
            'x': x_pos,
            'y': config.GROUND_Y,
            'size': size
        }
        enemy = Enemy(enemy_settings)

        # 左右に少し動く巡回アニメーション用のカスタム属性を追加
        enemy.patrol_center_x = x_pos
        enemy.patrol_range = 30
        enemy.patrol_speed = random.uniform(0.2, 0.6)
        enemy.patrol_direction = 1 if random.random() < 0.5 else -1
        
        self.decorative_enemies.append(enemy)
        self.spawn_count += 1 # スポーン数をインクリメント

    def process_event(self, event):
        """
        タイトル画面のイベントを処理する。
        :return: ゲーム開始のトリガー "START_GAME" または None
        """
        # Enterキーでも開始可能
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.audio_manager:
                self.audio_manager.play_ui_click_sound()
            return "START_GAME"
        
        # --- マウス・タッチ入力の統合 ---
        
        # 1. プレスダウン処理
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.FINGERDOWN:
            pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (event.x * config.SCREEN_WIDTH, event.y * config.SCREEN_HEIGHT)

            # スタートボタンがクリックされたか判定
            if self.start_button_rect.collidepoint(pos):
                if self.audio_manager:
                    self.audio_manager.play_ui_click_sound()
                return "START_GAME"

            # サウンドボタンがクリックされたか判定
            if self.sound_button_rect.collidepoint(pos):
                if self.audio_manager:
                    self.audio_manager.play_ui_click_sound()
                    self.audio_manager.toggle_enabled()
                return "TOGGLE_SOUND"

            # UI以外の場所をタッチしてドラッグ開始
            elif not self.bird.is_flying:
                self.is_dragging = True
                self.drag_start_pos = pygame.math.Vector2(pos) # タッチ開始点を記録
                self.mouse_pos.x, self.mouse_pos.y = pos
                self.show_drag_indicator = False # ドラッグを開始したら非表示に
                self.last_activity_time = pygame.time.get_ticks()

        # 2. ドラッグ中の移動処理
        if self.is_dragging and (event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION):
            pos = event.pos if event.type == pygame.MOUSEMOTION else (event.x * config.SCREEN_WIDTH, event.y * config.SCREEN_HEIGHT)
            self.mouse_pos.x, self.mouse_pos.y = pos

        # 3. リリース処理
        if self.is_dragging and ((event.type == pygame.MOUSEBUTTONUP and event.button == 1) or event.type == pygame.FINGERUP):
            pull_distance = self.slingshot_pos.distance_to(self.bird.pos)
            self.is_dragging = False
            if pull_distance > config.MIN_PULL_DISTANCE_TO_LAUNCH:
                launch_vector = self.slingshot_pos - self.bird.pos
                self.bird.launch(launch_vector)
                self.last_activity_time = pygame.time.get_ticks()
            else:
                self.bird.cancel_launch()
                print("Title Scene: Pull distance too short, launch cancelled.")
            self.trajectory_points.clear() # どちらの場合も軌道は消す

        return None

    def update(self):
        """タイトル画面のオブジェクトの状態を更新する。"""
        current_time = pygame.time.get_ticks()

        # ボールがちょうどリセットされた瞬間を検知
        if self.was_bird_flying and not self.bird.is_flying:
            self.last_activity_time = current_time
        self.was_bird_flying = self.bird.is_flying

        # 入力待機状態で一定時間経過したら、DRAG表示を再度有効にする
        if not self.is_dragging and not self.bird.is_flying:
            if current_time - self.last_activity_time > config.DRAG_PROMPT_DELAY:
                self.show_drag_indicator = True

        # --- ドラッグ中の処理を追加 ---
        if self.is_dragging:
            # ドラッグ開始点からのベクトルを計算
            drag_vector = self.mouse_pos - self.drag_start_pos
            # スリングショットの位置に、ドラッグベクトルを加算してボールを配置（直感的な引っ張り操作）
            self.bird.pos = self.slingshot_pos + drag_vector

            distance = self.slingshot_pos.distance_to(self.bird.pos)
            if distance > config.MAX_PULL_DISTANCE:
                if distance > 0:
                    direction = (self.bird.pos - self.slingshot_pos).normalize()
                    self.bird.pos = self.slingshot_pos + direction * config.MAX_PULL_DISTANCE
            # 軌道計算
            current_launch_vector = self.slingshot_pos - self.bird.pos
            self.trajectory_points = calculate_trajectory(self.bird.pos, current_launch_vector)
        elif self.bird.is_flying:
            # タイトル画面専用の更新処理をBirdクラスに委譲する
            self.bird.update_for_title_screen(self.slingshot_pos)

        # --- にぎやかし用の敵を時間差で出現させる ---
        can_spawn = len(self.decorative_enemies) < config.TITLE_ENEMY_MAX_COUNT
        time_to_spawn = current_time - self.last_enemy_spawn_time > config.TITLE_ENEMY_SPAWN_INTERVAL
        if can_spawn and time_to_spawn:
            self._spawn_decorative_enemy()
            self.last_enemy_spawn_time = current_time

        # にぎやかし用の敵を更新
        for enemy in self.decorative_enemies:
            # 横方向の巡回
            enemy.pos.x += enemy.patrol_speed * enemy.patrol_direction
            if abs(enemy.pos.x - enemy.patrol_center_x) > enemy.patrol_range:
                enemy.patrol_direction *= -1
            # 敵の内部状態（アニメーションなど）を更新させる
            enemy.update(tower=None, ground=self.ground)

    def draw(self, screen):
        """インタラクティブなタイトル画面を描画する。"""
        mouse_pos = pygame.mouse.get_pos()
        
        # --- カーソル形状の更新 ---
        is_start_hovered = self.start_button_rect.collidepoint(mouse_pos)
        is_sound_hovered = self.sound_button_rect.collidepoint(mouse_pos)
        if is_start_hovered or is_sound_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # --- インタラクティブ要素の描画 (奥) ---
        self.tower.draw(screen)

        for enemy in self.decorative_enemies:
            enemy.draw(screen)

        post_rect = pygame.Rect(self.slingshot_pos.x - config.SLINGSHOT_POST_WIDTH / 2, self.slingshot_pos.y, config.SLINGSHOT_POST_WIDTH, config.SLINGSHOT_POST_HEIGHT)
        pygame.draw.rect(screen, config.SLINGSHOT_POST_COLOR, post_rect)
        pygame.draw.rect(screen, config.BLACK, post_rect, 2)

        if self.is_dragging:
            for point in self.trajectory_points:
                pygame.draw.circle(screen, config.WHITE, (int(point.x), int(point.y)), config.TRAJECTORY_POINT_RADIUS)

            pygame.draw.line(screen, config.BLACK, self.slingshot_pos, self.bird.pos, 5)

        self.bird.draw(screen)

        # --- DRAG表示 (点滅) ---
        if self.show_drag_indicator and not self.is_dragging and not self.bird.is_flying:
            drag_text_pos = (self.bird.pos.x, self.bird.pos.y - self.bird.radius - 40)
            self.ui_manager.draw_blinking_text(
                "DRAG",
                drag_text_pos,
                config.BLACK,
                2
            )

        # --- UI要素の描画 (手前) ---
        draw_text(screen, "Babel's Tower Shooter", self.title_font, config.YELLOW, (config.SCREEN_WIDTH / 2, 100), config.BLACK, config.UI_TITLE_OUTLINE_WIDTH)

        # --- 操作説明エリアの描画 ---
        area_center_y = config.SCREEN_HEIGHT / 4 + 100 # y座標
        box_width = 450
        box_height = 100
        box_rect = pygame.Rect(0, 0, box_width, box_height)
        box_rect.center = (config.SCREEN_WIDTH * 2 / 4, area_center_y) # 操作説明ウィンドウの位置

        # 枠の背景（半透明）
        bg_surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 100)) # 半透明の黒
        screen.blit(bg_surface, box_rect.topleft)
        # 枠線
        pygame.draw.rect(screen, config.WHITE, box_rect, 2, border_radius=10)

        # 操作説明のタイトル
        title_y = box_rect.top + 30
        draw_text(screen, "- How To Play -", self.info_font, config.YELLOW, (box_rect.centerx, title_y), config.BLACK, 2)

        # 操作説明テキスト
        info_y = box_rect.top + 70
        draw_text(screen, "Drag & Release to Shoot the ball!", self.info_font, config.WHITE, (box_rect.centerx, info_y), config.BLACK, 2)

        # スタートボタン (地面と区別しやすいように色を変更)
        button_color = config.ORANGE_HOVER if is_start_hovered else config.ORANGE
        pygame.draw.rect(screen, button_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(screen, config.BLACK, self.start_button_rect, width=3, border_radius=15)
        draw_text(screen, "START", self.start_button_font, config.WHITE, self.start_button_rect.center, config.BLACK, 2)

        # ライセンス表示
        draw_text(screen, "Copyright 2025 k3 - MIT License", self.license_font, config.WHITE, (config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 20), config.BLACK, 1)

        # --- サウンドボタンの描画 ---
        if self.audio_manager:
            is_sound_on = self.audio_manager.enabled
            icon_text = "SOUND: ON" if is_sound_on else "SOUND: OFF"
            text_color = config.WHITE

            # 状態に応じてボタンの色を変更
            button_color = config.GREEN if is_sound_on else config.RED
            if is_sound_hovered:
                # ホバー時に少し明るくする
                r = min(255, button_color[0] + 30)
                g = min(255, button_color[1] + 30)
                b = min(255, button_color[2] + 30)
                button_color = (r, g, b)

            pygame.draw.rect(screen, button_color, self.sound_button_rect, border_radius=10)
            pygame.draw.rect(screen, config.BLACK, self.sound_button_rect, width=2, border_radius=10)
            draw_text(screen, icon_text, self.sound_button_font, text_color, self.sound_button_rect.center, config.BLACK, 2)
