import pygame
import config
import os
from typing import Dict, Any, List, Tuple

class AssetManager:
    """
    ゲームのアセット（画像、音声）の読み込みと管理を一元的に行うクラス。
    ローディング画面でこのクラスを使い、すべてのアセットを事前に読み込む。
    """
    def __init__(self):
        self.assets_to_load: List[Tuple[str, str, str, Any]] = []
        self.total_assets = 0
        self.loaded_assets = 0
        self.assets = {
            "images": {},
            "sounds": {}
        }
        self.sound_definitions: Dict[str, Dict[str, Any]] = {}
        self._define_assets()
        self._collect_assets()

    def _define_assets(self):
        """
        ゲーム内で使用するすべてのアセットの情報をここで一元管理する。
        これにより、ビルドツール(pygbag)がアセットを検出しやすくなる
        """
        # AudioManagerからse_pathsの定義を参考に、読み込むべきSEを定義
        self.sound_definitions = {
            "combo_hit": {"path": config.SE_COMBO_HIT_PATH, "volume": config.SE_COMBO_HIT_VOLUME},
            "enemy_death": {"path": config.SE_ENEMY_DEATH_PATH, "volume": config.SE_VOLUME},
            "enemy_hit": {"path": config.SE_ENEMY_HIT_PATH, "volume": config.SE_VOLUME},
            "tower_damage": {"path": config.SE_TOWER_DAMAGE_PATH, "volume": config.SE_VOLUME},
            "heart_collect": {"path": config.SE_HEART_COLLECT_PATH, "volume": config.SE_ITEM_COLLECT_VOLUME},
            "stage_start": {"path": config.SE_STAGE_START_PATH, "volume": config.SE_VOLUME},
            "ui_click": {"path": config.SE_UI_CLICK_PATH, "volume": config.SE_VOLUME},
            "item_spawn": {"path": config.SE_ITEM_SPAWN_PATH, "volume": config.SE_VOLUME},
            "speed_up_collect": {"path": config.SE_SPEED_UP_COLLECT_PATH, "volume": config.SE_ITEM_COLLECT_VOLUME},
            "size_up_collect": {"path": config.SE_SIZE_UP_COLLECT_PATH, "volume": config.SE_ITEM_COLLECT_VOLUME},
            "gauge_max": {"path": config.SE_GAUGE_MAX_PATH, "volume": config.SE_VOLUME},
        }

        # 音階SEを追加
        for i, path in enumerate(config.SCALE_SOUND_PATHS):
            key = f"scale_{i}"
            self.sound_definitions[key] = {"path": path, "volume": config.SE_VOLUME}

    def _collect_assets(self):
        """定義されたアセット情報を読み込みリストにまとめる。"""
        for key, props in self.sound_definitions.items():
            self.assets_to_load.append(('sound', key, props['path'], props['volume']))

        self.total_assets = len(self.assets_to_load)
        print(f"AssetManager: {self.total_assets}個のアセットを読み込みます。")

    def load_next_asset(self):
        """
        アセットを1つ読み込む。Webブラウザをフリーズさせないため、1フレームに1つずつ処理する。
        :return: まだ読み込むべきアセットが残っていればTrue、すべて完了したらFalse
        """
        if self.loaded_assets >= self.total_assets:
            return False

        asset_type, key, path, props = self.assets_to_load[self.loaded_assets]

        if asset_type == 'sound':
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(props) # props is volume for sounds
                    self.assets["sounds"][key] = sound
                except pygame.error as e:
                    print(f"エラー: SEファイル '{path}' の読み込みに失敗しました: {e}")
                    self.assets["sounds"][key] = None
            else:
                print(f"警告: SEファイルが見つかりません: {path}")
                self.assets["sounds"][key] = None

        self.loaded_assets += 1
        return True

    def get_progress(self):
        """読み込みの進捗を0.0から1.0の範囲で返す。"""
        if self.total_assets == 0:
            return 1.0
        return self.loaded_assets / self.total_assets

    def get_sound(self, key):
        """読み込み済みのSoundオブジェクトを取得する。"""
        return self.assets["sounds"].get(key)

    def disable_sound_loading(self):
        """音声の読み込みを無効にする。mixerの初期化に失敗した場合に呼ばれる。"""
        print("AssetManager: 音声の読み込みが無効化されました。")
        # 読み込みリストから音声アセットをフィルタリングして除外
        sound_count = len([asset for asset in self.assets_to_load if asset[0] == 'sound'])
        self.total_assets -= sound_count
        self.assets_to_load = [asset for asset in self.assets_to_load if asset[0] != 'sound']
