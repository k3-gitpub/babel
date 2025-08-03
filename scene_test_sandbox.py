import pygame
import asyncio
import config
import pygame_gui
from ground import Ground
from bird import Bird
from boss_enemy import BossEnemy

class SandboxUIManager:
    """サンドボックスシーンのUI要素の作成と管理を担当するクラス。"""
    def __init__(self, ui_manager, scene):
        self.ui_manager = ui_manager
        self.scene = scene # 親シーンへの参照
        pass
        
        # --- UI要素の作成 ---
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (100, 50)),
            text='Reset',
            manager=self.ui_manager
        )

        label_width = 240
        label_height = 30
        start_x = config.SCREEN_WIDTH - label_width - 10
        start_y = 10

        self.fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((start_x, start_y), (label_width, label_height)),
            text='FPS: -', manager=self.ui_manager
        )
        self.bird_pos_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((start_x, start_y + label_height), (label_width, label_height)),
            text='Bird Pos: (-, -)', manager=self.ui_manager
        )
        self.bird_vel_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((start_x, start_y + label_height * 2), (label_width, label_height)),
            text='Bird Vel: (-, -)', manager=self.ui_manager
        )
        self.boss_hp_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((start_x, start_y + label_height * 3), (label_width, label_height)),
            text='Boss HP: - / -', manager=self.ui_manager
        )

        self.gravity_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 70), (200, 30)),
            start_value=config.GRAVITY, value_range=(0.1, 2.0), manager=self.ui_manager
        )
        self.gravity_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((220, 70), (100, 30)),
            text=f"Gravity: {config.GRAVITY:.2f}", manager=self.ui_manager
        )

        self.bird_radius_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, 110), (200, 30)), manager=self.ui_manager
        )
        self.bird_radius_entry.set_text(str(config.BIRD_DEFAULT_RADIUS))
        self.bird_radius_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((220, 110), (100, 30)),
            text="Bird Radius", manager=self.ui_manager
        )

    def process_events(self, event):
        """UI関連のイベントを処理する。"""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.reset_button:
                self.scene._reset_objects()
        
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.gravity_slider:
                self.scene.current_gravity = event.value
                self.gravity_label.set_text(f"Gravity: {self.scene.current_gravity:.2f}")
        
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.bird_radius_entry:
                try:
                    new_radius = float(event.text)
                    if new_radius > 0:
                        self.scene.bird.radius = new_radius
                        self.scene.bird._update_stats()
                        self.scene.bird._create_image()
                        print(f"Bird radius set to {new_radius}")
                    else:
                        self.bird_radius_entry.set_text(str(self.scene.bird.radius))
                except ValueError:
                    self.bird_radius_entry.set_text(str(self.scene.bird.radius))

    def update(self):
        """デバッグ用ラベルのテキストを更新する。"""
        self.fps_label.set_text(f"FPS: {self.scene.clock.get_fps():.1f}")
        self.bird_pos_label.set_text(f"Bird Pos: ({self.scene.bird.pos.x:.1f}, {self.scene.bird.pos.y:.1f})")
        self.bird_vel_label.set_text(f"Bird Vel: ({self.scene.bird.velocity.x:.1f}, {self.scene.bird.velocity.y:.1f})")
        self.boss_hp_label.set_text(f"Boss HP: {self.scene.boss.hp:.0f} / {self.scene.boss.max_hp:.0f}")

    def reset_ui_values(self):
        """UIの値をオブジェクトの状態に合わせてリセットする。"""
        self.gravity_slider.set_current_value(self.scene.current_gravity)
        self.gravity_label.set_text(f"Gravity: {self.scene.current_gravity:.2f}")
        self.bird_radius_entry.set_text(str(self.scene.bird.radius))

class TestSandboxScene:
    """
    特定の機能（例：敵のAI）を単体でテストするための軽量なシーン。
    """
    def __init__(self):
        """テストシーンを初期化する。"""
        # pygbagの非同期環境でpygameを初期化するためのおまじない
        # これがないと、Web上でリソースの準備が完了する前にinit()が呼ばれてしまうことがある
        # asyncio.run(asyncio.sleep(0)) # これはrun()の外では使えない

        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Test Sandbox - LeftClick: Teleport, RightClick: Launch, R: Reset")
        self.clock = pygame.time.Clock()
        self.running = True

        # --- pygame-guiのセットアップ ---
        gui_manager = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), theme_path='theme.json')
        self.ui = SandboxUIManager(gui_manager, self)

        # --- テスト対象のオブジェクトを初期化 ---
        self.ground = Ground()
        self._reset_objects() # ヘルパーメソッドで初期化とリセットを共通化

    def _reset_objects(self):
        """テスト用のオブジェクトを初期位置にリセットする。"""
        # ボスはステータス倍率1.0で生成
        self.boss = BossEnemy(stat_multiplier={})
        # ボールは適当な位置に配置
        self.bird = Bird(200, 400, config.BIRD_DEFAULT_RADIUS)

        # UIの値もリセット
        self.current_gravity = config.GRAVITY
        if hasattr(self, 'ui'):
            self.ui.reset_ui_values()

        print("Sandbox objects have been reset.")

    def handle_events(self, time_delta):
        """イベントを処理する。"""
        # get()はイベントキューから全てのイベントを取得するリストを返す
        # これをループで処理することで、全てのイベントに対応できる
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # --- UIマネージャーにイベントを渡す ---
            self.ui.ui_manager.process_events(event)
            self.ui.process_events(event)

            # --- キーボード入力 ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._reset_objects()

            # --- マウス入力 ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # UI要素の上でクリックされた場合は、ゲーム内操作を無視する
                if self.ui.ui_manager.get_focus_set() is not None:
                    continue

                mouse_pos = pygame.math.Vector2(event.pos)
                # 左クリック: ボールをテレポート
                if event.button == 1:
                    self.bird.pos = mouse_pos
                    self.bird.velocity.update(0, 0) # 速度をリセット
                    self.bird.is_flying = False # 飛行状態を解除
                    print(f"Bird teleported to {mouse_pos}")

                # 右クリック: ボールを発射
                elif event.button == 3:
                    launch_vector = mouse_pos - self.bird.pos
                    self.bird.launch(launch_vector)
                    print(f"Bird launched with vector {launch_vector}")

    def update(self, time_delta):
        """オブジェクトの状態を更新する。"""
        # UIマネージャーの更新
        self.ui.ui_manager.update(time_delta)
        self.ui.update()

        self.ground.update()
        # ボスはタワーなし、地面ありで更新
        self.boss.update(tower=None, ground=self.ground)
        self.bird.update(gravity=self.current_gravity)


    def draw(self):
        """画面を描画する。"""
        # 背景は通常と違う色にして、テストシーンであることが分かるようにする
        self.screen.fill(config.GRAY)

        self.ground.draw(self.screen)
        self.boss.draw(self.screen)
        self.bird.draw(self.screen)

        # UIをゲームオブジェクトの上に描画
        self.ui.ui_manager.draw_ui(self.screen)

        pygame.display.flip()

    async def run(self):
        """このシーン専用のメインループ。"""
        # pygbagの非同期環境でpygameを初期化するためのおまじない
        # runループの開始時に一度だけ実行する
        await asyncio.sleep(0)

        while self.running:
            time_delta = self.clock.tick(config.FPS) / 1000.0
            self.handle_events(time_delta)
            self.update(time_delta)
            self.draw()

            await asyncio.sleep(0)

        pygame.quit()
        print("Test Sandbox Scene finished.")
