import pygame
import config
from ui_utils import draw_text

class LoadingScene:
    """
    ゲームのアセット読み込み中に表示されるローディング画面を管理するクラス。
    """
    def __init__(self, ui_manager, asset_manager):
        """
        LoadingSceneを初期化する。
        :param ui_manager: UI描画に使用するUIManagerのインスタンス
        :param asset_manager: アセットの読み込み状況を管理するAssetManagerのインスタンス
        """
        self.ui_manager = ui_manager
        self.asset_manager = asset_manager
        self.title_font = pygame.font.Font(None, 72)
        self.progress_font = pygame.font.Font(None, 36)

    def update(self):
        """
        アセットの読み込みを1フレーム分進める。
        :return: 読み込みが完了したら "LOADING_COMPLETE" を返す。
        """
        is_still_loading = self.asset_manager.load_next_asset()
        if not is_still_loading:
            return "LOADING_COMPLETE"
        return None

    def draw(self, screen):
        """ローディング画面（テキスト、プログレスバー）を描画する。"""
        screen.fill(config.BLUE)

        draw_text(screen, "Now Loading...", self.title_font, config.WHITE,
                  (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 - 50),
                  config.BLACK, 2)

        progress = self.asset_manager.get_progress()
        bar_width = 400
        bar_height = 30
        bar_x = (config.SCREEN_WIDTH - bar_width) / 2
        bar_y = config.SCREEN_HEIGHT / 2 + 20

        pygame.draw.rect(screen, config.GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        progress_width = bar_width * progress
        pygame.draw.rect(screen, config.WHITE, (bar_x, bar_y, progress_width, bar_height), border_radius=5)
        pygame.draw.rect(screen, config.BLACK, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)

        percent_text = f"{int(progress * 100)}%"
        draw_text(screen, percent_text, self.progress_font, config.BLACK,
                  (config.SCREEN_WIDTH / 2, bar_y + bar_height / 2))

