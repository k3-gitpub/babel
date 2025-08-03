import pygame
import asyncio
import config
from ui_utils import draw_text

class MobileTest:
    """
    モバイルブラウザでの音声再生をテストするための最小クラス。
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
        """イベントを処理し、入力があった瞬間に音声処理を試みる。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "WAITING_FOR_INPUT":
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN]:
                    print("Input detected! Attempting to initialize audio and play sound.")
                    try:
                        # --- 音声関連の処理をすべてこのイベントハンドラ内で完結させる ---
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
        """状態に応じて画面を描画する。"""
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
        """メインループ。"""
        while self.running:
            await self._handle_events()
            self._draw_screen()
            await asyncio.sleep(0)
            self.clock.tick(config.FPS)

async def main():
    test = MobileTest()
    await test.run()

if __name__ == '__main__':
    asyncio.run(main())
