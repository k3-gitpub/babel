import pygame
import config
from ui_utils import draw_text

class EndScreen:
    """ゲームオーバー/クリア時のリザルト画面の描画を担当するクラス。"""
    def __init__(self, screen, title_font, result_font, boss_font):
        self.screen = screen
        self.title_font = title_font
        self.result_font = result_font
        self.boss_font = boss_font
        self.button_font = pygame.font.Font(None, 48) # ボタン用のフォント

        # リスタートボタンのRectを定義 (位置はdrawメソッド内で動的に決定)
        button_width, button_height = 240, 60
        self.restart_button_rect = pygame.Rect(0, 0, button_width, button_height)

    def draw(self, stage_state, score=0, high_score=0, max_combo=0, best_combo=0, tower_height=0, tower_bonus=0, best_tower_height=0, mouse_pos=(0,0)):
        """
        ステージクリアまたはゲームオーバーの画面を描画する。
        :param stage_state: 現在のステージの状態 ("CLEARING", "GAME_OVER", "GAME_WON")
        """
        if stage_state == "CLEARING": # ステージクリア時はメッセージのみ
            draw_text(
                self.screen,
                "STAGE CLEAR",
                self.title_font,
                config.YELLOW,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2),
                config.BLACK,
                config.UI_TITLE_OUTLINE_WIDTH
            )
        elif stage_state in ["GAME_OVER", "GAME_WON"]:
            # --- メインメッセージ (GAME OVER / GAME CLEAR) ---
            if stage_state == "GAME_OVER":
                message = "GAME OVER"
                color = config.RED
            else: # GAME_WON
                message = "GAME CLEAR!"
                color = config.AQUA

            draw_text(
                self.screen,
                message, self.title_font, color,
                (config.SCREEN_WIDTH / 2, 100), # 少し上に表示
                config.BLACK, config.UI_TITLE_OUTLINE_WIDTH
            )

            # --- リザルト表示 ---
            result_start_y = config.SCREEN_HEIGHT / 2 - 150 # 全体をさらに少し上に
            line_height = 42
            current_y = result_start_y

            # スコア
            draw_text(
                self.screen,
                f"SCORE: {score}", self.result_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, current_y),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            current_y += line_height

            # ハイスコア
            is_new_high_score = score > high_score
            high_score_color = config.YELLOW if is_new_high_score else config.WHITE
            high_score_text = f"HIGH SCORE: {high_score if not is_new_high_score else score}"
            draw_text(
                self.screen,
                high_score_text, self.result_font, high_score_color,
                (config.SCREEN_WIDTH / 2, current_y),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            if is_new_high_score:
                draw_text(
                    self.screen,
                    "NEW RECORD!", self.boss_font, config.YELLOW,
                    (config.SCREEN_WIDTH / 2 + 300, current_y),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )
            current_y += line_height * 1.5 # スコア項目とタワー項目を少し離す

            # タワー関連の表示 (GAME_WONの時のみ)
            if stage_state == "GAME_WON":
                draw_text(
                    self.screen,
                    f"TOWER HEIGHT: {tower_height} Blocks", self.result_font, config.WHITE,
                    (config.SCREEN_WIDTH / 2, current_y),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )
                current_y += line_height
                draw_text(
                    self.screen,
                    f"TOWER BONUS: +{tower_bonus}", self.result_font, config.YELLOW,
                    (config.SCREEN_WIDTH / 2, current_y),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )
                current_y += line_height

                # 最高のタワーの高さ
                is_new_best_height = tower_height > best_tower_height
                best_height_color = config.YELLOW if is_new_best_height else config.WHITE
                best_height_text = f"BEST HEIGHT: {best_tower_height if not is_new_best_height else tower_height}"
                draw_text(
                    self.screen,
                    best_height_text, self.result_font, best_height_color,
                    (config.SCREEN_WIDTH / 2, current_y),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )
                if is_new_best_height:
                    draw_text(
                        self.screen, "NEW RECORD!", self.boss_font, config.YELLOW,
                        (config.SCREEN_WIDTH / 2 + 300, current_y), config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH)
                current_y += line_height * 1.5 # タワー項目とコンボ項目を少し離す

            # 最大コンボ
            draw_text(
                self.screen,
                f"MAX COMBO: {max_combo}", self.result_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, current_y),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            current_y += line_height

            # ベストコンボ
            is_new_best_combo = max_combo > best_combo
            best_combo_color = config.YELLOW if is_new_best_combo else config.WHITE
            best_combo_text = f"BEST COMBO: {best_combo if not is_new_best_combo else max_combo}"
            draw_text(
                self.screen,
                best_combo_text, self.result_font, best_combo_color,
                (config.SCREEN_WIDTH / 2, current_y),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            if is_new_best_combo:
                draw_text(
                    self.screen,
                    "NEW RECORD!", self.boss_font, config.YELLOW,
                    (config.SCREEN_WIDTH / 2 + 300, current_y),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )
            current_y += line_height * 1.5 # 少し間隔をあける

            # --- リスタートボタンの描画 ---
            self.restart_button_rect.center = (config.SCREEN_WIDTH / 2, current_y + 30)
            is_hovered = self.restart_button_rect.collidepoint(mouse_pos)
            button_color = config.ORANGE_HOVER if is_hovered else config.ORANGE
            button_text = "RESTART" if stage_state == "GAME_OVER" else "PLAY AGAIN"

            pygame.draw.rect(self.screen, button_color, self.restart_button_rect, border_radius=15)
            pygame.draw.rect(self.screen, config.BLACK, self.restart_button_rect, width=3, border_radius=15)
            draw_text(self.screen, button_text, self.button_font, config.WHITE, self.restart_button_rect.center, config.BLACK, 2)