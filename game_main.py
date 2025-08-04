# Copyright 2025 k3
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import asyncio # Webアプリ(Pygbag)化のために追加
from game import Game

print("--- EXECUTING main.py ---")

async def main():
    """
    ゲームを起動するための非同期メイン関数。
    Webビルド時にアセットを登録する処理もここで行う。
    """
    # --- Webビルド(pygbag)のためのアセット登録と初期化 ---
    try:
        from pygbag import preloader
        await preloader.run(log_missing=True)
    except ImportError:
        # pygbagがインストールされていないローカル実行環境では何もしない
        pass

    game = Game()
    await game.run()

if __name__ == '__main__':
    asyncio.run(main())
