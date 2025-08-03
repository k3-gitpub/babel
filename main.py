import pygame
import asyncio
import config
from ui_utils import draw_text
from scene_title import TitleScene
from asset_manager import AssetManager
from loading_scene import LoadingScene

class Game:
    """
    ゲームの骨格をテストするためのクラス。
    状態管理と文字描画のみを実装する。
    """
    def __init__(self):
        # 基本的なPygameの初期化
        pygame.display.init()
        pygame.font.init()
        self.mixer_initialized = False # 音声が初期化されたかのフラグ

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Step 4: Asset Loading Test")
        self.clock = pygame.time.Clock()
        self.running = True

        # 状態管理
        self.game_state = "WAITING_FOR_INPUT"
        self.title_scene = None
        self.loading_scene = None
        self.asset_manager = AssetManager()

        # 「Click to Start」メッセージ用のフォント
        self.title_font = pygame.font.Font(None, 120)

    def _initialize_audio(self):
        """ユーザーの最初のインタラクションでオーディオシステムを初期化する。"""
        if self.mixer_initialized:
            return

        print("ユーザーの初回入力により、オーディオシステムを初期化します。")
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"警告: Pygame mixerの初期化に失敗しました: {e}")
            self.mixer_initialized = False

    async def _handle_events(self):
        """イベントを処理する。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 入力待ち状態で、マウスクリック、タッチ、キー入力があった場合
            if self.game_state == "WAITING_FOR_INPUT":
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN]:
                    self._initialize_audio() # ★★★ 音声初期化をここで行う ★★★
                    print("Input detected! Changing state to LOADING.")
                    self.game_state = "LOADING"
                    self.loading_scene = LoadingScene(self.asset_manager)

    async def _update_state(self):
        """ゲームの状態に基づいてロジックを更新する。"""
        if self.game_state == "LOADING":
            if self.loading_scene:
                action = self.loading_scene.update()
                if action == "LOADING_COMPLETE":
                    print("Loading complete! Changing state to TITLE.")
                    self.game_state = "TITLE"
                    self.title_scene = TitleScene(self.asset_manager)

    def _draw_screen(self):
        """状態に応じて画面を描画する。"""
        if self.game_state == "WAITING_FOR_INPUT":
            self.screen.fill(config.BLUE)
            # テキストを点滅させる
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                draw_text(self.screen, "Click to Start", self.title_font, config.WHITE,
                          (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), config.BLACK, 3)
        elif self.game_state == "LOADING":
            self.screen.fill(config.BLUE)
            if self.loading_scene:
                self.loading_scene.draw(self.screen)
        elif self.game_state == "TITLE":
            # タイトルシーンを描画
            self.screen.fill(config.BLUE)
            if self.title_scene:
                self.title_scene.draw(self.screen)

        pygame.display.flip()

    async def run(self):
        """ゲームのメインループ。"""
        while self.running:
            await self._handle_events()
            await self._update_state()
            self._draw_screen()
            await asyncio.sleep(0)
            self.clock.tick(config.FPS)

async def main():
    game = Game()
    await game.run()

if __name__ == '__main__':
    asyncio.run(main())
