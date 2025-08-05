# Copyright 2025 k3
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import asyncio # Webアプリ(Pygbag)化のために追加
from game import Game

print("--- EXECUTING main.py ---")

async def main():
    """
    Asynchronous main function to launch the game.
    This is also where assets are registered for the web build.
    """
    # --- Asset registration and initialization for web build (pygbag) ---
    try:
        from pygbag import preloader
        await preloader.run(log_missing=True)
    except ImportError:
        # Do nothing in a local execution environment where pygbag is not installed
        pass

    game = Game()
    await game.run()

if __name__ == '__main__':
    asyncio.run(main())
