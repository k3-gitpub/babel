import pygame
import config
from bird import Bird
from tower import Tower
from game_logic import calculate_trajectory
import random
from enemy import Enemy
from ground import Ground

class TitleScene:
    """
    インタラクティブなタイトル画面を管理するクラス。
    プレイヤーはここで基本操作を試すことができる。
    """
    def __init__(self, ui_manager):
        """
        TitleSceneを初期化する。
        :param ui_manager: UI描画に使用するUIManagerのインスタンス
        """
        self.ui_manager = ui_manager
        self.title_font = pygame.font.Font(None, 90) # タイトル用に少し小さめのフォント
        self.license_font = pygame.font.Font(None, 24) # ライセンス表示用のフォント
        self.info_font = pygame.font.Font(None, 36) # 操作説明用のフォント
        self.start_button_font = pygame.font.Font(None, 48) # スタートボタン専用のフォント

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
            return "START_GAME"
        
        # --- マウス操作を追加 ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # スタートボタンがクリックされたか判定
            if self.start_button_rect.collidepoint(event.pos):
                return "START_GAME"
            
            if self.bird.is_clicked(event.pos):
                self.is_dragging = True
                self.mouse_pos.x, self.mouse_pos.y = event.pos
                self.show_drag_indicator = False # ドラッグを開始したら非表示に
                self.last_activity_time = pygame.time.get_ticks()
        
        if event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.mouse_pos.x, self.mouse_pos.y = event.pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_dragging:
            self.is_dragging = False
            # ボールを発射する
            launch_vector = self.slingshot_pos - self.bird.pos
            self.bird.launch(launch_vector)
            self.last_activity_time = pygame.time.get_ticks()
            self.trajectory_points.clear()

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
            self.bird.pos = self.mouse_pos.copy()
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
        # マウスカーソルがボタン上にあるか判定
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.start_button_rect.collidepoint(mouse_pos)

        # カーソルの形状を変更
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)

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
        self.ui_manager._draw_text("Babel's Tower Shooter", self.title_font, config.YELLOW, (config.SCREEN_WIDTH / 2, 100), config.BLACK, config.UI_TITLE_OUTLINE_WIDTH)

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
        self.ui_manager._draw_text("- How To Play -", self.info_font, config.YELLOW, (box_rect.centerx, title_y), config.BLACK, 2)

        # 操作説明テキスト
        info_y = box_rect.top + 70
        self.ui_manager._draw_text("Drag & Release to Shoot the ball!", self.info_font, config.WHITE, (box_rect.centerx, info_y), config.BLACK, 2)

        # スタートボタン (地面と区別しやすいように色を変更)
        button_color = config.ORANGE_HOVER if is_hovered else config.ORANGE
        pygame.draw.rect(screen, button_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(screen, config.BLACK, self.start_button_rect, width=3, border_radius=15)
        self.ui_manager._draw_text("START", self.start_button_font, config.WHITE, self.start_button_rect.center, config.BLACK, 2)

        # ライセンス表示
        self.ui_manager._draw_text("Copyright 2025 k3 - MIT License", self.license_font, config.WHITE, (config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 20), config.BLACK, 1)
