import pygame
import math
import config

class ComboIndicator:
    """
    画面に表示されるコンボテキストの情報を保持するデータクラス。
    アニメーションに必要な情報（位置、テキスト、表示開始時間など）を管理する。
    """
    def __init__(self, position, combo_count: int):
        self.pos = position.copy()
        self.start_y = position.y # アニメーションの開始Y座標
        self.combo_count = combo_count
        self.start_time = pygame.time.get_ticks()

class UIManager:
    """
    ゲームのUI要素（テキスト、カウンター、メッセージなど）の描画を管理するクラス。
    """
    def __init__(self, screen, ui_font, title_font, boss_font, combo_font):
        """
        UIManagerを初期化する。
        :param screen: 描画対象のPygame screenオブジェクト
        :param ui_font: UI用のフォント
        :param title_font: タイトル用のフォント
        :param boss_font: ボス戦用のフォント
        :param combo_font: コンボ表示用のフォント
        """
        self.screen = screen
        self.ui_font = ui_font
        self.title_font = title_font
        self.boss_font = boss_font
        self.combo_font = combo_font
        self.combo_indicators = [] # 表示中のコンボテキストを保持するリスト

    def add_combo_indicator(self, position, combo_count):
        """
        新しいコンボ表示をリストに追加する。
        ステップ5でGameLogicManagerから呼び出される。
        :param position: 表示を開始する位置 (Vector2)
        :param combo_count: 表示するコンボ数 (int)
        """
        indicator = ComboIndicator(position, combo_count)
        self.combo_indicators.append(indicator)
        # 動作確認用のプリント
        print(f"UI: Added combo indicator for 'x{indicator.combo_count} COMBO!' at {indicator.pos}")

    def _draw_text(self, text, font, color, center_pos, outline_color=None, outline_width=0, alpha=None):
        """指定された位置に中央揃えでアウトライン付きテキストを描画する。アルファ（透明度）も指定可能。"""
        # アウトラインの描画
        if outline_color and outline_width > 0:
            outline_surface = font.render(text, True, outline_color)
            if alpha is not None:
                outline_surface.set_alpha(alpha)
            # 8方向にオフセットして描画
            offsets = [
                (dx, dy) for dx in range(-outline_width, outline_width + 1, outline_width) 
                         for dy in range(-outline_width, outline_width + 1, outline_width) 
                         if not (dx == 0 and dy == 0)
            ]
            # 8方向ではなく4方向（斜め）に描画して負荷を軽減
            # offsets = [(-outline_width, -outline_width), (-outline_width, outline_width), (outline_width, -outline_width), (outline_width, outline_width)]

            for dx, dy in offsets:
                outline_rect = outline_surface.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                self.screen.blit(outline_surface, outline_rect)

        # 本体のテキストを描画
        text_surface = font.render(text, True, color)
        if alpha is not None:
            text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=center_pos)
        self.screen.blit(text_surface, text_rect)

    def _draw_heart(self, center_x, center_y, size, color):
        """指定された位置にハートを描画する。"""
        points = []
        for t_deg in range(0, 360):
            t_rad = math.radians(t_deg)
            scale = size / 32.0
            dx = 16 * (math.sin(t_rad) ** 3)
            dy = -(13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
            x = center_x + dx * scale
            y = center_y + dy * scale
            points.append((x, y))
        pygame.draw.polygon(self.screen, color, points)

    def _draw_boss_hp_bar(self, boss, boss_name):
        """ボスのHPバーを描画する。"""
        bar_width = config.BOSS_HP_BAR_WIDTH
        bar_height = config.BOSS_HP_BAR_HEIGHT
        bar_x = (config.SCREEN_WIDTH - bar_width) / 2
        bar_y = config.BOSS_HP_BAR_Y

        # HPの割合を計算
        hp_ratio = boss.hp / boss.max_hp if boss.max_hp > 0 else 0
        current_hp_width = bar_width * hp_ratio

        # --- HPバーの描画 ---
        # 背景
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, config.BOSS_HP_BAR_BG_COLOR, bg_rect, border_radius=5)

        # HPバー本体
        if current_hp_width > 0:
            hp_rect = pygame.Rect(bar_x, bar_y, current_hp_width, bar_height)
            pygame.draw.rect(self.screen, config.BOSS_HP_BAR_COLOR, hp_rect, border_radius=5)

        # 枠線
        pygame.draw.rect(self.screen, config.BLACK, bg_rect, config.BOSS_HP_BAR_OUTLINE_WIDTH, border_radius=5)

        # --- ボスの名前を描画 (HPバーの後) ---
        # HPバーの上、中央に配置
        name_pos = (bar_x + bar_width / 2, bar_y + config.BOSS_NAME_OFFSET_Y)
        self._draw_text(
            boss_name,
            self.boss_font,
            config.WHITE,
            name_pos,
            config.BLACK,
            config.UI_COUNTER_OUTLINE_WIDTH
        )

        # HPテキスト
        hp_text = f"{int(boss.hp)} / {int(boss.max_hp)}"
        # HPバー用の小さいフォント
        hp_font = pygame.font.Font(None, 24)
        # self._draw_text(hp_text, hp_font, config.WHITE, bg_rect.center, config.BLACK, 1)

    def draw_game_hud(self, tower, enemies_defeated_count, enemies_to_clear, current_stage, boss=None, boss_name=None):
        """
        ゲーム中のHUD（ヘッドアップディスプレイ）を描画する。
        これにはタワーのライフや討伐数カウンターが含まれる。
        """
        # --- 現在のステージ番号を描画 ---
        stage_text = f"STAGE {current_stage}"
        self._draw_text(
            stage_text,
            self.ui_font,
            config.WHITE,
            (150, 40), # 画面左上に表示
            config.BLACK,
            config.UI_COUNTER_OUTLINE_WIDTH
        )

        # --- タワーのライフ（ブロック数）を描画 ---
        # ブロックの数がタワーのライフを直接表現する
        num_lives = len(tower.blocks)

        if num_lives > 0:
            for i in range(int(num_lives)):
                heart_x = config.TOWER_HEART_START_X + i * config.TOWER_HEART_SPACING
                # 画面外にはみ出さないようにする
                if heart_x > config.SCREEN_WIDTH - config.TOWER_HEART_SIZE:
                    break
                self._draw_heart(
                    heart_x, config.TOWER_HEART_Y, config.TOWER_HEART_SIZE, config.TOWER_HEART_COLOR
                )

        if boss and boss_name:
            # --- ボス戦UI ---
            self._draw_text(
                "BOSS BATTLE", self.boss_font, config.BOSS_UI_TITLE_COLOR,
                (config.SCREEN_WIDTH - 160, 40),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            self._draw_boss_hp_bar(boss, boss_name)
        else:
            # --- 通常UI (討伐数カウンター) ---
            counter_text = f"{enemies_defeated_count}/{enemies_to_clear}"
            self._draw_text(
                counter_text, self.ui_font, config.WHITE,
                (config.SCREEN_WIDTH - 100, 40), config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

    def draw_end_screen(self, stage_state):
        """
        ステージクリアまたはゲームオーバーの画面を描画する。
        :param stage_state: 現在のステージの状態 ("CLEARING", "GAME_OVER", "GAME_WON")
        """
        if stage_state == "CLEARING":
            self._draw_text(
                "STAGE CLEAR", 
                self.title_font, 
                config.YELLOW, 
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2),
                config.BLACK,
                config.UI_TITLE_OUTLINE_WIDTH
            )
        elif stage_state == "GAME_OVER":
            self._draw_text(
                "GAME OVER", self.title_font, config.RED,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2),
                config.BLACK, config.UI_TITLE_OUTLINE_WIDTH
            )
            self._draw_text(
                "Press 'R' to Restart", self.ui_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 80),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
        elif stage_state == "GAME_WON":
            self._draw_text(
                "GAME CLEAR!", self.title_font, config.AQUA,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2),
                config.BLACK, config.UI_TITLE_OUTLINE_WIDTH
            )
            self._draw_text(
                "Press 'R' to Play Again", self.ui_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 80),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

    def draw_recall_button(self, position):
        """
        弾を呼び戻すための「Recall」ボタンを描画する。
        :param position: ボタンを描画する中心座標 (Vector2)
        :return: 描画したボタンのRectオブジェクト
        """
        button_width, button_height = config.RECALL_BUTTON_SIZE
        button_rect = pygame.Rect(
            position.x - button_width / 2,
            position.y - button_height / 2,
            button_width,
            button_height
        )

        # 角丸の四角形を描画
        pygame.draw.rect(self.screen, config.RECALL_BUTTON_COLOR, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, config.BLACK, button_rect, width=2, border_radius=10)

        # メソッド内で小さいフォントを生成してテキストを描画
        font = pygame.font.Font(None, 36)
        self._draw_text("RECALL", font, config.RECALL_BUTTON_TEXT_COLOR, button_rect.center, config.BLACK, 1)

        return button_rect

    def _draw_combo_indicators(self):
        """表示中のコンボテキストをアニメーション付きで描画し、古いものを削除する。"""
        current_time = pygame.time.get_ticks()

        # --- 描画処理 (正順ループ) ---
        # リストの先頭から描画することで、後から追加されたもの（新しいもの）が手前に描画される
        for indicator in self.combo_indicators:
            elapsed_time = current_time - indicator.start_time

            # 寿命が過ぎたものは描画しない
            if elapsed_time > config.COMBO_DURATION:
                continue

            # --- アニメーション計算 ---
            # 進行度 (0.0 -> 1.0)
            progress = min(elapsed_time / config.COMBO_DURATION, 1.0)

            # 1. 位置 (下から上へ)
            current_y = indicator.start_y - (config.COMBO_MOVE_Y * progress)
            current_pos = (indicator.pos.x, current_y)

            # 2. 色 (開始色から終了色へ線形補間)
            r = config.COMBO_START_COLOR[0] + (config.COMBO_END_COLOR[0] - config.COMBO_START_COLOR[0]) * progress
            g = config.COMBO_START_COLOR[1] + (config.COMBO_END_COLOR[1] - config.COMBO_START_COLOR[1]) * progress
            b = config.COMBO_START_COLOR[2] + (config.COMBO_END_COLOR[2] - config.COMBO_START_COLOR[2]) * progress
            current_color = (r, g, b)

            # 3. 透明度 (不透明 -> 透明)
            alpha = 255 * (1.0 - progress)

            # --- テキストとフォントの準備 ---
            prefix_text = "x"
            number_text = str(indicator.combo_count)
            suffix_text = " COMBO!"

            # コンボ数に応じて数字のフォントサイズを動的に変更
            additional_size = min(
                int(indicator.combo_count * config.COMBO_NUMBER_SCALE_FACTOR),
                config.COMBO_NUMBER_MAX_ADDITIONAL_SIZE
            )
            number_font_size = config.COMBO_NUMBER_BASE_FONT_SIZE + additional_size
            number_font = pygame.font.Font(None, number_font_size)

            # --- 各パーツのSurfaceを計算（位置合わせのため） ---
            prefix_surf = self.combo_font.render(prefix_text, True, current_color)
            number_surf = number_font.render(number_text, True, current_color)
            suffix_surf = self.combo_font.render(suffix_text, True, current_color)

            # --- 全体の幅を計算し、描画開始位置を決定 ---
            total_width = prefix_surf.get_width() + number_surf.get_width() + suffix_surf.get_width()
            start_x = current_pos[0] - total_width / 2

            # --- 各パーツを描画 ---
            # 1. プレフィックス ("x")
            prefix_center_x = start_x + prefix_surf.get_width() / 2
            self._draw_text(
                prefix_text, self.combo_font, current_color,
                (prefix_center_x, current_pos[1]),
                config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, alpha
            )

            # 2. 数字 (コンボ数)
            number_center_x = start_x + prefix_surf.get_width() + number_surf.get_width() / 2
            self._draw_text(
                number_text, number_font, current_color,
                (number_center_x, current_pos[1]),
                config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, alpha
            )

            # 3. サフィックス (" COMBO!")
            suffix_center_x = start_x + prefix_surf.get_width() + number_surf.get_width() + suffix_surf.get_width() / 2
            self._draw_text(
                suffix_text, self.combo_font, current_color,
                (suffix_center_x, current_pos[1]),
                config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, alpha
            )

        # --- 削除処理 ---
        # 寿命が尽きたインジケーターをリストから一括で削除する
        self.combo_indicators = [
            indicator for indicator in self.combo_indicators
            if (current_time - indicator.start_time) <= config.COMBO_DURATION
        ]

    def draw_ui_overlays(self):
        """HUDや他のUI要素の上に描画されるべき要素（コンボ表示など）をまとめて描画する。"""
        self._draw_combo_indicators()
