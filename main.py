import pygame
import asyncio

# --- 依存をなくすため、定数を直接定義 ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BLUE = (66, 165, 245)
RED = (211, 47, 47)
MAGENTA = (255, 0, 255) # エラー表示用の色

async def main():
    screen = None
    try:
        # --- 最小限の初期化と初回描画 ---
        pygame.display.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("iPhone Static Draw Test")
        clock = pygame.time.Clock()

        # 画面を青で塗りつぶし、中央に赤い四角形を描画
        screen.fill(BLUE)
        pygame.draw.rect(screen, RED, ((SCREEN_WIDTH - 100) / 2, (SCREEN_HEIGHT - 100) / 2, 100, 100))
        pygame.display.flip()
        print("Initial draw completed. Entering event loop.")

        # --- イベントループ (描画は初回のみ) ---
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            await asyncio.sleep(0)
            clock.tick(60)

    except Exception as e:
        # エラーが発生した場合、画面をマゼンタ色にする試み
        print(f"A fatal error occurred: {e}")
        try:
            if screen is None:
                pygame.display.init()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.fill(MAGENTA)
            pygame.display.flip()
            while True: await asyncio.sleep(0.1)
        except Exception:
            pass

if __name__ == '__main__':
    asyncio.run(main())
