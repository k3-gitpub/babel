import pygame
import asyncio
import sys

# 画面サイズ
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 色
BLUE = (66, 165, 245)
RED = (211, 47, 47)

async def main():
    # Webブラウザとの互換性のため、ディスプレイモジュールだけを明示的に初期化
    pygame.display.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minimal Pygbag Test")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 画面を青で塗りつぶし、中央に赤い四角形を描画
        screen.fill(BLUE)
        pygame.draw.rect(screen, RED, ((SCREEN_WIDTH - 100) / 2, (SCREEN_HEIGHT - 100) / 2, 100, 100))
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())