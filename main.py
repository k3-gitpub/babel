import pygame
import asyncio

# --- 依存をなくすため、定数を直接定義 ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BLUE = (66, 165, 245)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

async def main():
    screen = None
    try:
        # --- ステップ1: ディスプレイの初期化のみ ---
        pygame.display.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultimate Core Test")
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
                screen.fill(BLUE)
            elif state == 1:
                screen.fill(GREEN)

            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(60)

    except Exception as e:
        try:
            if screen is None:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.fill(RED)
            pygame.display.flip()
            while True: await asyncio.sleep(0.1)
        except Exception as e2:
            pass # エラー表示すら失敗


if __name__ == '__main__':
    asyncio.run(main())
