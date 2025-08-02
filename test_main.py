import pygame
import asyncio
import sys

# 画面サイズ
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 色
WHITE = (255, 255, 255)
BLUE = (66, 165, 245)
RED = (211, 47, 47)

async def main():
    # pygame.init()は全てのモジュールを初期化しようとして失敗する可能性がある。
    # 問題を切り分けるため、ディスプレイモジュールだけを明示的に初期化する。
    pygame.display.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygbag Barebones Test")
    clock = pygame.time.Clock()
    running = True

    print("Barebones Test Program Started. Only display module initialized.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # 描画
        screen.fill(BLUE)
        # フォントを使わずに、画面中央に四角形を描画するだけ
        rect_width = 400
        rect_height = 200
        rect_x = (SCREEN_WIDTH - rect_width) / 2
        rect_y = (SCREEN_HEIGHT - rect_height) / 2
        pygame.draw.rect(screen, RED, (rect_x, rect_y, rect_width, rect_height))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())