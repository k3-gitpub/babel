import pygame
import asyncio
import config
import traceback

async def main():
    """
    モバイル環境でPygameのコア機能（表示とイベント）が動作するかを確認する最小テスト。
    フォントやサウンドの読み込みを一切行わない。
    """
    screen = None
    try:
        # --- ステップ1: ディスプレイの初期化のみ ---
        pygame.display.init()
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Mobile Core Test")
        clock = pygame.time.Clock()
        print("Display initialized successfully.")

        # --- ステップ2: 最小限のメインループ ---
        running = True
        # 0: 入力待ち(青), 1: 成功(緑)
        state = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # 状態で分岐し、最初のタップ/クリック/キー入力で状態を1にする
                if state == 0 and event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN]:
                    print("Input detected! The event loop is working.")
                    state = 1

            # --- 状態に応じて画面の色を変える ---
            if state == 0:
                screen.fill(config.BLUE)
            elif state == 1:
                screen.fill(config.GREEN)

            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(config.FPS)

    except Exception as e:
        # このブロックは、上記の最小限の処理ですら失敗した場合に実行される
        print("--- A FATAL CORE INITIALIZATION ERROR OCCURRED ---")
        traceback.print_exc()
        # 失敗したことを示すために、画面を赤くする試み
        try:
            if screen is None:
                screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            screen.fill(config.RED)
            pygame.display.flip()
            while True: await asyncio.sleep(0.1)
        except Exception as e2:
            print(f"FATAL: Could not even display the red error screen: {e2}")


if __name__ == '__main__':
    asyncio.run(main())
