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

    def draw(self, stage_state, score=0, high_score=0, max_combo=0, best_combo=0):
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
                restart_text = "Press 'R' to Restart"
            else: # GAME_WON
                message = "GAME CLEAR!"
                color = config.AQUA
                restart_text = "Press 'R' to Play Again"

            draw_text(
                self.screen,
                message, self.title_font, color,
                (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 - 150), # 少し上に表示
                config.BLACK, config.UI_TITLE_OUTLINE_WIDTH
            )

            # --- リザルト表示 ---
            result_start_y = config.SCREEN_HEIGHT / 2 - 50
            line_height = 50

            # スコア
            draw_text(
                self.screen,
                f"SCORE: {score}", self.result_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, result_start_y),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

            # ハイスコア
            is_new_high_score = score > high_score
            high_score_color = config.YELLOW if is_new_high_score else config.WHITE
            high_score_text = f"HIGH SCORE: {high_score if not is_new_high_score else score}"
            draw_text(
                self.screen,
                high_score_text, self.result_font, high_score_color,
                (config.SCREEN_WIDTH / 2, result_start_y + line_height),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )
            if is_new_high_score:
                draw_text(
                    self.screen,
                    "NEW RECORD!", self.boss_font, config.YELLOW,
                    (config.SCREEN_WIDTH / 2 + 300, result_start_y + line_height),
                    config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
                )

            # 最大コンボ
            draw_text(
                self.screen,
                f"MAX COMBO: {max_combo}", self.result_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, result_start_y + line_height * 2.5),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

            # ベストコンボ
            is_new_best_combo = max_combo > best_combo
            best_combo_color = config.YELLOW if is_new_best_combo else config.WHITE
            best_combo_text = f"BEST COMBO: {best_combo if not is_new_best_combo else max_combo}"
            draw_text(
                self.screen,
                best_combo_text, self.result_font, best_combo_color,
                (config.SCREEN_WIDTH / 2, result_start_y + line_height * 3.5),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )

            # --- リスタート案内 ---
            draw_text(
                self.screen,
                restart_text, self.result_font, config.WHITE,
                (config.SCREEN_WIDTH / 2, result_start_y + line_height * 5),
                config.BLACK, config.UI_COUNTER_OUTLINE_WIDTH
            )