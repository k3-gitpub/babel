import pygame
import asyncio
import config
from ui_utils import draw_text
import traceback

async def main():
    """
    メインの実行部分。初期化を含むすべての処理をエラー監視下に置く。
    """
    screen = None
    try:
        # --- ステップ1: 最小限のPygame初期化 ---
        pygame.display.init()
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Mobile Init Test")
        clock = pygame.time.Clock()

        # --- ステップ2: 問題の可能性が最も高いフォントの初期化 ---
        print("Attempting to initialize font system...")
        pygame.font.init()
        font = pygame.font.Font(None, 100)
        info_font = pygame.font.Font(None, 40)
        print("Font system initialized successfully.")

        # --- ステップ3: 音声の準備 (まだ実行はしない) ---
        sound = None
        sound_path = config.SE_UI_CLICK_PATH

        # --- メインループ ---
        running = True
        game_state = "WAITING_FOR_INPUT"
        error_message = ""

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if game_state == "WAITING_FOR_INPUT":
                    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN]:
                        print("Input detected! Attempting to initialize audio and play sound.")
                        try:
                            pygame.mixer.init()
                            sound = pygame.mixer.Sound(sound_path)
                            sound.play()
                            game_state = "SUCCESS"
                        except Exception as e:
                            print(f"An error occurred during sound playback: {e}")
                            error_message = str(e)
                            game_state = "FAILURE"

            # --- 描画処理 ---
            if game_state == "WAITING_FOR_INPUT":
                screen.fill(config.BLUE)
                draw_text(screen, "Tap to Test Sound", font, config.WHITE,
                          (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), config.BLACK, 3)
            elif game_state == "SUCCESS":
                screen.fill(config.GREEN)
                draw_text(screen, "Success!", font, config.WHITE,
                          (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), config.BLACK, 3)
            elif game_state == "FAILURE":
                screen.fill(config.RED)
                draw_text(screen, "Sound Failure!", font, config.WHITE,
                          (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 - 40), config.BLACK, 3)
                draw_text(screen, error_message, info_font, config.WHITE,
                          (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 40), config.BLACK, 2)

            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(config.FPS)

    except Exception as e:
        # ★★★ 初期化を含む、すべてのエラーがここで捕捉される ★★★
        print("--- A FATAL INITIALIZATION ERROR OCCURRED ---")
        traceback.print_exc()
        print("---------------------------------------------")

        try:
            if screen is None:
                pygame.display.init()
                screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            
            screen.fill(config.RED)

            # エラー表示用のフォントも、失敗する可能性を考慮してtry-exceptで囲む
            error_font, error_font_small = None, None
            try:
                error_font = pygame.font.Font(None, 32)
                error_font_small = pygame.font.Font(None, 24)
            except Exception as font_error:
                print(f"Could not load font for error display: {font_error}")

            # エラーメッセージを整形して描画
            error_message = f"FATAL ERROR: {e}"
            lines = [error_message[i:i+80] for i in range(0, len(error_message), 80)]
            
            y = 50
            if error_font:
                draw_text(screen, "An error occurred during init.", error_font, config.WHITE, (config.SCREEN_WIDTH/2, y))
                y += 50
                for line in lines:
                    draw_text(screen, line, error_font_small, config.WHITE, (config.SCREEN_WIDTH/2, y))
                    y += 30
            
            pygame.display.flip()

            # ユーザーが確認できるよう、エラー画面を表示し続ける
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return
                await asyncio.sleep(0.1)

        except Exception as e2:
            print(f"FATAL: Could not even display the error on screen: {e2}")


if __name__ == '__main__':
    asyncio.run(main())
