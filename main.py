import pygame
import asyncio
import config
from ui_utils import draw_text
import traceback # エラーの詳細情報を取得するために追加

class MobileTest:
    """
    モバイルブラウザでの音声再生をテストするための最小クラス。
    （このクラスの中身は前回と同じです）
    """
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Mobile Sound Test")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "WAITING_FOR_INPUT"
        self.font = pygame.font.Font(None, 100)
        self.info_font = pygame.font.Font(None, 40)
        self.sound = None
        self.error_message = ""

    async def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "WAITING_FOR_INPUT":
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN]:
                    print("Input detected! Attempting to initialize audio and play sound.")
                    try:
                        pygame.mixer.init()
                        print("pygame.mixer.init() successful.")
                        
                        sound_path = config.SE_UI_CLICK_PATH
                        print(f"Attempting to load sound: {sound_path}")
                        self.sound = pygame.mixer.Sound(sound_path)
                        print("Sound loaded successfully.")
                        
                        self.sound.play()
                        print("Sound played successfully.")
                        
                        self.game_state = "SUCCESS"
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        self.error_message = str(e)
                        self.game_state = "FAILURE"

    def _draw_screen(self):
        if self.game_state == "WAITING_FOR_INPUT":
            self.screen.fill(config.BLUE)
            draw_text(self.screen, "Tap to Test Sound", self.font, config.WHITE,
                      (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), config.BLACK, 3)
        elif self.game_state == "SUCCESS":
            self.screen.fill(config.GREEN)
            draw_text(self.screen, "Success!", self.font, config.WHITE,
                      (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), config.BLACK, 3)
            draw_text(self.screen, "Sound played.", self.info_font, config.WHITE,
                      (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 80), config.BLACK, 2)
        elif self.game_state == "FAILURE":
            self.screen.fill(config.RED)
            draw_text(self.screen, "Failure!", self.font, config.WHITE,
                      (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 - 40), config.BLACK, 3)
            draw_text(self.screen, self.error_message, self.info_font, config.WHITE,
                      (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 40), config.BLACK, 2)

        pygame.display.flip()

    async def run(self):
        while self.running:
            await self._handle_events()
            self._draw_screen()
            await asyncio.sleep(0)
            self.clock.tick(config.FPS)

async def main():
    """
    メインの実行部分。ここでエラーを捕捉し、画面に表示する。
    """
    try:
        # 通常通りゲームを実行
        test = MobileTest()
        await test.run()
    except Exception as e:
        # ★★★ もしプログラムのどこかでエラーが起きたら、ここが実行される ★★★
        print("--- A FATAL ERROR OCCURRED ---")
        traceback.print_exc() # コンソールに詳細なエラー情報を出力
        print("-----------------------------")

        # 画面にエラーを表示する試み
        try:
            # Pygameが初期化されていなくても、ここで初期化を試みる
            if not pygame.display.get_init(): pygame.display.init()
            if not pygame.font.get_init(): pygame.font.init()

            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            screen.fill(config.RED) # 背景を赤に

            font = pygame.font.Font(None, 32)
            font_small = pygame.font.Font(None, 24)

            # エラーメッセージを整形して描画
            error_message = f"FATAL ERROR: {e}"
            # 長いメッセージを折り返す
            lines = [error_message[i:i+80] for i in range(0, len(error_message), 80)]
            
            y = 50
            draw_text(screen, "An error occurred and the game stopped.", font, config.WHITE, (config.SCREEN_WIDTH/2, y))
            y += 50

            for line in lines:
                draw_text(screen, line, font_small, config.WHITE, (config.SCREEN_WIDTH/2, y))
                y += 30

            pygame.display.flip()

            # ユーザーが確認できるよう、エラー画面を表示し続ける
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return
                await asyncio.sleep(0.1)

        except Exception as e2:
            # エラー画面の表示すら失敗した場合
            print(f"Could not display the error on screen: {e2}")


if __name__ == '__main__':
    asyncio.run(main())
