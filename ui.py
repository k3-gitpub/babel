import pygame
import math
import config
from ui_utils import draw_text, draw_heart
from end_screen import EndScreen

class ComboIndicator:
    """
    画面に表示されるコンボテキストの情報を保持し、
    アニメーションと描画のロジックを自己完結して持つクラス。
    """
    def __init__(self, position, combo_count: int):
        self.start_pos = position.copy()
        self.combo_count = combo_count
        self.start_time = pygame.time.get_ticks()
        self.alive = True

        # アニメーション中の状態を保持するプロパティ
        self.current_pos = self.start_pos.copy()
        self.current_color = config.COMBO_START_COLOR
        self.alpha = 255

    def update(self):
        """アニメーションの状態を更新する。寿命が尽きたらaliveフラグをFalseにする。"""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > config.COMBO_DURATION:
            self.alive = False
            return

        progress = min(elapsed_time / config.COMBO_DURATION, 1.0)

        # 位置 (下から上へ)
        self.current_pos.y = self.start_pos.y - (config.COMBO_MOVE_Y * progress)

        # 色 (開始色から終了色へ線形補間)
        r = config.COMBO_START_COLOR[0] + (config.COMBO_END_COLOR[0] - config.COMBO_START_COLOR[0]) * progress
        g = config.COMBO_START_COLOR[1] + (config.COMBO_END_COLOR[1] - config.COMBO_START_COLOR[1]) * progress
        b = config.COMBO_START_COLOR[2] + (config.COMBO_END_COLOR[2] - config.COMBO_START_COLOR[2]) * progress
        self.current_color = (r, g, b)

        # 透明度 (不透明 -> 透明)
        self.alpha = 255 * (1.0 - progress)

    def draw(self, screen, combo_font):
        """自身の現在の状態に基づいて描画する。"""
        prefix_text = "x"
        number_text = str(self.combo_count)
        suffix_text = " COMBO!"

        # コンボ数に応じて数字のフォントサイズを動的に変更
        additional_size = min(
            int(self.combo_count * config.COMBO_NUMBER_SCALE_FACTOR),
            config.COMBO_NUMBER_MAX_ADDITIONAL_SIZE
        )
        number_font_size = config.COMBO_NUMBER_BASE_FONT_SIZE + additional_size
        number_font = pygame.font.Font(None, number_font_size)

        # 各パーツのSurfaceを計算（位置合わせのため）
        prefix_surf = combo_font.render(prefix_text, True, self.current_color)
        number_surf = number_font.render(number_text, True, self.current_color)
        suffix_surf = combo_font.render(suffix_text, True, self.current_color)

        # 全体の幅を計算し、描画開始位置を決定
        total_width = prefix_surf.get_width() + number_surf.get_width() + suffix_surf.get_width()
        start_x = self.current_pos.x - total_width / 2

        # 各パーツを描画
        prefix_center_x = start_x + prefix_surf.get_width() / 2
        draw_text(screen, prefix_text, combo_font, self.current_color, (prefix_center_x, self.current_pos.y), config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, self.alpha)

        number_center_x = start_x + prefix_surf.get_width() + number_surf.get_width() / 2
        draw_text(screen, number_text, number_font, self.current_color, (number_center_x, self.current_pos.y), config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, self.alpha)

        suffix_center_x = start_x + prefix_surf.get_width() + number_surf.get_width() + suffix_surf.get_width() / 2
        draw_text(screen, suffix_text, combo_font, self.current_color, (suffix_center_x, self.current_pos.y), config.COMBO_OUTLINE_COLOR, config.COMBO_OUTLINE_WIDTH, self.alpha)

    @property
    def is_alive(self):
        return self.alive

class ScoreIndicator:
    """
    画面に表示されるスコアテキストの情報を保持するデータクラス。
    アニメーションと描画のロジックを自己完結して持つ。
    """
    def __init__(self, position, text: str):
        self.start_pos = position.copy()
        self.text = text
        self.start_time = pygame.time.get_ticks()
        self.alive = True

        # アニメーション中の状態を保持するプロパティ
        self.current_pos = self.start_pos.copy()
        self.alpha = 255

    def update(self):
        """アニメーションの状態を更新する。寿命が尽きたらaliveフラグをFalseにする。"""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > config.SCORE_INDICATOR_DURATION:
            self.alive = False
            return

        # 進行度 (0.0 -> 1.0)
        progress = min(elapsed_time / config.SCORE_INDICATOR_DURATION, 1.0)
        # 位置を更新 (下から上へ)
        self.current_pos.y = self.start_pos.y - (config.SCORE_INDICATOR_MOVE_Y * progress)
        # 透明度を更新 (不透明 -> 透明)
        self.alpha = 255 * (1.0 - progress)

    def draw(self, screen, font):
        """自身の現在の状態に基づいて描画する。"""
        draw_text(
            screen,
            self.text,
            font,
            config.SCORE_INDICATOR_COLOR,
            self.current_pos,
            config.SCORE_INDICATOR_OUTLINE_COLOR,
            config.SCORE_INDICATOR_OUTLINE_WIDTH,
            self.alpha
        )

    @property
    def is_alive(self):
        return self.alive

class HUD:
    """ゲーム中の通常HUD（スコア、ライフなど）の描画を担当するクラス。"""
    def __init__(self, screen, ui_font, boss_font):
        self.screen = screen
        self.ui_font = ui_font
        self.boss_font = boss_font

    def draw(self, tower, current_stage, max_combo_count, current_score):
        """
        ゲーム中の共通HUD（ステージ、スコア、コンボ、ライフ）を描画する。
        """
        # --- 現在のステージ番号を描画 ---
        stage_text = f"STAGE {current_stage}"
        draw_text(
            self.screen,
            stage_text,
            self.ui_font,
            config.WHITE,
            (150, 40), # 画面左上に表示
            config.BLACK,
            config.UI_COUNTER_OUTLINE_WIDTH
        )

        # --- 最大コンボ数を描画 ---
        if max_combo_count > 0:
            max_combo_text = f"MAX COMBO: {max_combo_count}"
            draw_text(
                self.screen,
                max_combo_text,
                self.boss_font, # ステージ番号より少し小さいフォント
                config.YELLOW,
                (config.SCREEN_WIDTH - 150, 80), # 画面右上に表示
                config.BLACK,
                config.UI_COUNTER_OUTLINE_WIDTH
            )

        # --- 現在のスコアを描画 ---
        score_text = f"SCORE: {current_score}"
        draw_text(
            self.screen,
            score_text,
            self.boss_font, # MAX COMBOと同じフォントサイズ
            config.WHITE,
            (150, 80), # ステージ番号の下に表示
            config.BLACK,
            config.UI_COUNTER_OUTLINE_WIDTH
        )

        # --- タワーのライフ（ブロック数）を描画 ---
        num_lives = len(tower.blocks)
        if num_lives > 0:
            for i in range(int(num_lives)):
                heart_x = config.TOWER_HEART_START_X + i * config.TOWER_HEART_SPACING
                if heart_x > config.SCREEN_WIDTH - config.TOWER_HEART_SIZE:
                    break
                draw_heart(self.screen, heart_x, config.TOWER_HEART_Y, config.TOWER_HEART_SIZE, config.TOWER_HEART_COLOR)

class BossHUD:
    """ボス戦専用のHUD（HPバーなど）の描画を担当するクラス。"""
    def __init__(self, screen, boss_font):
        self.screen = screen
        self.boss_font = boss_font

    def draw(self, boss, boss_name):
        """ボス戦のUIを描画する。"""
        # --- "BOSS BATTLE" テキスト ---
        draw_text(
            self.screen,
            "BOSS BATTLE", self.boss_font, config.BOSS_UI_TITLE_COLOR,
            (config.SCREEN_WIDTH - 160, 40),
            config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
        )

        # --- HPバー ---
        bar_width = config.BOSS_HP_BAR_WIDTH
        bar_height = config.BOSS_HP_BAR_HEIGHT
        bar_x = (config.SCREEN_WIDTH - bar_width) / 2
        bar_y = config.BOSS_HP_BAR_Y

        hp_ratio = boss.hp / boss.max_hp if boss.max_hp > 0 else 0
        current_hp_width = bar_width * hp_ratio

        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, config.BOSS_HP_BAR_BG_COLOR, bg_rect, border_radius=5)

        if current_hp_width > 0:
            hp_rect = pygame.Rect(bar_x, bar_y, current_hp_width, bar_height)
            pygame.draw.rect(self.screen, config.BOSS_HP_BAR_COLOR, hp_rect, border_radius=5)

        pygame.draw.rect(self.screen, config.BLACK, bg_rect, config.BOSS_HP_BAR_OUTLINE_WIDTH, border_radius=5)

        name_pos = (bar_x + bar_width / 2, bar_y + config.BOSS_NAME_OFFSET_Y)
        draw_text(
            self.screen,
            boss_name, self.boss_font, config.WHITE,
            name_pos, config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
        )

class UIManager:
    """
    ゲームのUI要素（テキスト、カウンター、メッセージなど）の描画を管理するクラス。
    """
    def __init__(self, screen, ui_font, title_font, boss_font, combo_font, result_font):
        """
        UIManagerを初期化する。
        :param screen: 描画対象のPygame screenオブジェクト
        :param ui_font: UI用のフォント
        :param title_font: タイトル用のフォント
        :param boss_font: ボス戦用のフォント
        :param combo_font: コンボ表示用のフォント
        :param result_font: リザルト画面用のフォント
        """
        self.screen = screen
        self.ui_font = ui_font
        self.title_font = title_font
        self.boss_font = boss_font
        self.combo_font = combo_font
        self.drag_font = pygame.font.Font(None, config.DRAG_TEXT_FONT_SIZE) # DRAG表示用のフォント
        self.score_font = pygame.font.Font(None, config.SCORE_INDICATOR_FONT_SIZE) # スコアポップアップ用
        self.combo_indicators = [] # 表示中のコンボテキストを保持するリスト
        self.score_indicators = [] # 表示中のスコアテキストを保持するリスト

        # --- ステップC-1: HUDクラスのインスタンス化 ---
        self.hud = HUD(self.screen, self.ui_font, self.boss_font)

        # --- ステップC-2: BossHUDクラスのインスタンス化 ---
        self.boss_hud = BossHUD(self.screen, self.boss_font)

        # --- ステップC-4: EndScreenクラスのインスタンス化 ---
        self.end_screen = EndScreen(self.screen, self.title_font, result_font, self.boss_font)

    def update(self):
        """UI要素の状態（アニメーションなど）を更新し、不要なものを削除する。"""
        # --- ScoreIndicatorの更新 ---
        for indicator in self.score_indicators:
            indicator.update()

        # --- ComboIndicatorの更新 ---
        for indicator in self.combo_indicators:
            indicator.update()

        self.combo_indicators = [ind for ind in self.combo_indicators if ind.is_alive]
        # 寿命が尽きたものをリストから削除
        self.score_indicators = [ind for ind in self.score_indicators if ind.is_alive]

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
        print(f"UI: Added combo indicator for 'x{indicator.combo_count} COMBO!' at {indicator.start_pos}")

    def add_score_indicator(self, position, score_value):
        """
        新しいスコア表示をリストに追加する。
        :param position: 表示を開始する位置 (Vector2)
        :param score_value: 表示するスコア値 (int)
        """
        text = f"+{score_value}"
        indicator = ScoreIndicator(position, text)
        self.score_indicators.append(indicator)

    def draw_boss_hud(self, boss, boss_name):
        """ボス戦専用のHUDを描画する。内部でBossHUDクラスのdrawを呼び出す。"""
        self.boss_hud.draw(boss, boss_name)

    def draw_game_hud(self, tower, enemies_defeated_count, enemies_to_clear, current_stage, max_combo_count, current_score, boss=None, boss_name=None):
        """
        ゲーム中のHUD（ヘッドアップディスプレイ）を描画する。
        共通HUDを描画し、状況に応じて通常カウンターかボスHUDを描画する。
        """
        # 1. 共通のHUD要素（スコア、ライフなど）をHUDクラスに描画させる
        self.hud.draw(tower, current_stage, max_combo_count, current_score)

        # 2. ボス戦かどうかで、描画するUIを切り替える
        if boss and boss_name:
            # --- ボス戦UI ---
            self.draw_boss_hud(boss, boss_name)
        else:
            # --- 通常UI (討伐数カウンター) ---
            counter_text = f"{enemies_defeated_count}/{enemies_to_clear}"
            draw_text(
                self.screen,
                counter_text, self.ui_font, config.WHITE,
                (config.SCREEN_WIDTH - 100, 40), config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

    def draw_end_screen(self, stage_state, score=0, high_score=0, max_combo=0, best_combo=0):
        """
        ステージクリアまたはゲームオーバーの画面を描画する。
        内部でEndScreenクラスのdrawを呼び出す。
        """
        self.end_screen.draw(stage_state, score, high_score, max_combo, best_combo)

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
        draw_text(self.screen, "RECALL", font, config.RECALL_BUTTON_TEXT_COLOR, button_rect.center, config.BLACK, 1)

        return button_rect

    def _draw_combo_indicators(self):
        """表示中のコンボテキストをアニメーション付きで描画し、古いものを削除する。"""
        # 各インジケーターに自身の描画を依頼する
        for indicator in self.combo_indicators:
            indicator.draw(self.screen, self.combo_font)

    def _draw_score_indicators(self):
        """表示中のスコアテキストをアニメーション付きで描画し、古いものを削除する。"""
        # 各インジケーターに自身の描画を依頼するだけのシンプルなループになる
        for indicator in self.score_indicators:
            indicator.draw(self.screen, self.score_font)

    def draw_ui_overlays(self):
        """HUDや他のUI要素の上に描画されるべき要素（コンボ表示など）をまとめて描画する。"""
        self._draw_score_indicators() # 先にスコアを描画（奥に表示される）
        self._draw_combo_indicators() # 後からコンボを描画（手前に表示される）

    def draw_blinking_text(self, text, center_pos, outline_color=None, outline_width=0):
        """
        指定されたテキストを点滅描画する。
        :param text: 描画する文字列
        :param center_pos: 描画する中心座標
        :param outline_color: アウトラインの色
        :param outline_width: アウトラインの太さ
        """
        # 現在の時間を使って表示/非表示を切り替える
        # (現在時間 // 点滅間隔) の結果が偶数か奇数かで判定
        if (pygame.time.get_ticks() // config.DRAG_TEXT_BLINK_INTERVAL) % 2 == 0:
            draw_text(
                self.screen,
                text,
                self.drag_font,
                config.DRAG_TEXT_COLOR,
                center_pos,
                outline_color,
                outline_width
            )
