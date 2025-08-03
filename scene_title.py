import pygame
import config
from ui_utils import draw_text

class TitleScene:
    """
    ステップ3用の最小限のタイトルシーンクラス。
    静的なテキストを描画するだけ。
    """
    def __init__(self, asset_manager):
        """TitleSceneを初期化し、フォントを準備する。"""
        self.asset_manager = asset_manager
        self.title_font = pygame.font.Font(None, 120)
        self.button_font = pygame.font.Font(None, 60)

    def draw(self, screen):
        """タイトル画面の静的な要素を描画する。"""
        # ゲームタイトルを描画
        draw_text(screen, "Babel's Tower Shooter", self.title_font, config.YELLOW,
                  (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 3), config.BLACK, 3)

        # 静的な「START」ボタンを描画（このステップではクリック不可）
        draw_text(screen, "START", self.button_font, config.WHITE,
                  (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT * 2 / 3), config.BLACK, 2)