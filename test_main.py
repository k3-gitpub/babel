import pygame
import asyncio
import sys

# 画面サイズ
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 色
WHITE = (255, 255, 255)
BLUE = (66, 165, 245)
BLACK = (0, 0, 0)

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygbag Simple Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)
    running = True

    print("Simple Test Program Started")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # 描画
        screen.fill(BLUE)
        
        text_surface = font.render("Pygbag Simple Test", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(text_surface, text_rect)

        info_font = pygame.font.Font(None, 48)
        info_surface = info_font.render("If you see this, Pygbag is working.", True, WHITE)
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        screen.blit(info_surface, info_rect)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())