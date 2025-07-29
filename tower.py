import pygame
import config
import math
from block import Block

class Tower:
    """
    複数のブロックで構成されるタワーを管理するクラス。ブロックの落下や破壊を管理する。
    """
    def __init__(self, base_x, ground_y, top_y):
        """
        タワーを初期化する。
        :param base_x: タワーの土台の左端のX座標
        :param ground_y: 地面のY座標
        :param top_y: タワーのてっぺんのY座標
        """
        self.base_x = base_x
        self.ground_y = ground_y
        self.blocks = []
        block_width = config.TOWER_BLOCK_WIDTH
        block_height = config.TOWER_BLOCK_HEIGHT

        # タワーの本来のブロック数を計算して保存
        self.original_num_blocks = int((ground_y - top_y) / block_height)
        for i in range(self.original_num_blocks):
            block_x = base_x
            block_y = ground_y - (i + 1) * block_height
            self.blocks.append(Block(block_x, block_y, block_width, block_height))

    def update(self):
        """
        タワーを構成する全てのブロックを更新する。
        破壊されたブロックを検知し、その上のブロックを落下させる。
        """
        # 1. 各ブロックの内部状態（アニメーション、落下物理）を更新する
        for i, block in enumerate(self.blocks):
            # 自分より下にあるブロックのリストを渡す
            blocks_below = self.blocks[:i]
            block.update(blocks_below, self.ground_y)

        # 2. 破壊アニメーションが完了したブロックをリストから削除する
        #    リストを逆順に走査することで、安全に要素を削除できる
        for i in range(len(self.blocks) - 1, -1, -1):
            if self.blocks[i].is_finished():
                # ブロックをリストから削除
                del self.blocks[i]

                # 削除によって生じた隙間の上にあるブロック全てを落下させる
                # 削除後のリストのインデックス`i`から末尾までが対象
                for j in range(i, len(self.blocks)):
                    self.blocks[j].start_falling()

    def draw(self, screen):
        """タワーを構成する全てのブロックを描画する。"""
        for block in self.blocks:
            block.draw(screen)

    def get_top_y(self):
        """タワーの一番上のブロックのてっぺんのY座標を返す。ブロックがなければ地面のY座標を返す。"""
        if not self.blocks:
            return self.ground_y
        # Y座標が最も小さい（画面上で最も上にある）ブロックのtopを返す
        return min(block.rect.top for block in self.blocks)

    def is_destroyed(self):
        """タワーが完全に破壊された（ブロックが一つも残っていない）か判定する。"""
        return not self.blocks

    def repair_one_block(self):
        """
        タワーのブロックを1つ修復/追加する。
        修復に成功した場合はTrueを返す。
        """
        # 新しいブロックの位置を計算
        # 既存のブロックの一番上、もしくはブロックがなければ地面の上
        new_block_top_y = self.get_top_y() - config.TOWER_BLOCK_HEIGHT

        # 新しいブロックを作成してリストの末尾に追加（一番上に追加される）
        new_block = Block(self.base_x, new_block_top_y, config.TOWER_BLOCK_WIDTH, config.TOWER_BLOCK_HEIGHT)
        self.blocks.append(new_block)

        # ブロックが正しく層になるように、Y座標でソートする（下から上へ）
        self.blocks.sort(key=lambda b: b.rect.y, reverse=True)

        print("タワーを1ブロック修復/追加しました！")
        return True
