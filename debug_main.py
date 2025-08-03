# Copyright 2025 k3
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import asyncio # Webアプリ(Pygbag)化のために追加
from game import Game

if __name__ == '__main__':
    # ステージ3（ボスステージ）から直接開始する
    game = Game(start_stage=3)
    # Gameクラスの非同期メソッドrun()を実行
    asyncio.run(game.run())
