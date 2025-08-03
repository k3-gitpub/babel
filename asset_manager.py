import pygame
import config
import os
from typing import Dict, Any, List, Tuple

class AssetManager:
    """
    ステップ4用のアセット管理クラス。
    少数のサウンドアセットを段階的に読み込む。
    """
    def __init__(self):
        self.assets_to_load: List[Tuple[str, str, str, Any]] = []
        self.total_assets = 0
        self.loaded_assets = 0
        self.assets = {
            "sounds": {}
        }
        self._define_assets()
        self._collect_assets()

    def _define_assets(self):
        """テスト用に少数のサウンドアセットを定義する。"""
        if not config.DISABLE_SOUND_FOR_DEBUG:
            self.sound_definitions = {
                "ui_click": {"path": "assets/audio/select.ogg", "volume": config.SE_VOLUME},
                "enemy_death": {"path": "assets/audio/explosion.ogg", "volume": config.SE_VOLUME},
                "enemy_hit": {"path": "assets/audio/dead.ogg", "volume": config.SE_VOLUME},
            }
        else:
            self.sound_definitions = {}

    def _collect_assets(self):
        """定義されたアセット情報を読み込みリストにまとめる。"""
        for key, props in self.sound_definitions.items():
            self.assets_to_load.append(('sound', key, props['path'], props['volume']))

        self.total_assets = len(self.assets_to_load)
        print(f"AssetManager: {self.total_assets}個のアセットを読み込みます。")

    def load_next_asset(self):
        """アセットを1つ読み込む。"""
        if self.loaded_assets >= self.total_assets:
            return False

        asset_type, key, path, props = self.assets_to_load[self.loaded_assets]
        print(f"Loading asset {self.loaded_assets + 1}/{self.total_assets}: [{asset_type}] {key} at {path}")

        if asset_type == 'sound' and os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(props)
                self.assets["sounds"][key] = sound
            except pygame.error as e:
                print(f"エラー: SEファイル '{path}' の読み込みに失敗しました: {e}")

        self.loaded_assets += 1
        return True

    def get_progress(self):
        """読み込みの進捗を0.0から1.0の範囲で返す。"""
        if self.total_assets == 0: return 1.0
        return self.loaded_assets / self.total_assets