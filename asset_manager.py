import pygame
import config
import os

class AssetManager:
    """
    ゲームのアセット（画像、音声）の読み込みと管理を一元的に行うクラス。
    ローディング画面でこのクラスを使い、すべてのアセットを事前に読み込む。
    """
    def __init__(self):
        self.images_to_load = []
        self.sounds_to_load = []
        self.total_assets = 0
        self.loaded_assets = 0
        self.assets = {
            "images": {},
            "sounds": {}
        }
        self._collect_asset_paths()

    def _collect_asset_paths(self):
        """
        ゲーム内で使用するすべてのアセットのパスを収集する。
        """
        # AudioManagerからse_pathsの定義を参考に、読み込むべきSEを定義
        se_definitions = {
            "combo_hit": (config.SE_COMBO_HIT_PATH, config.SE_COMBO_HIT_VOLUME),
            "enemy_death": (config.SE_ENEMY_DEATH_PATH, config.SE_VOLUME),
            "enemy_hit": (config.SE_ENEMY_HIT_PATH, config.SE_VOLUME),
            "tower_damage": (config.SE_TOWER_DAMAGE_PATH, config.SE_VOLUME),
            "heart_collect": (config.SE_HEART_COLLECT_PATH, config.SE_ITEM_COLLECT_VOLUME),
            "stage_start": (config.SE_STAGE_START_PATH, config.SE_VOLUME),
            "ui_click": (config.SE_UI_CLICK_PATH, config.SE_VOLUME),
            "item_spawn": (config.SE_ITEM_SPAWN_PATH, config.SE_VOLUME),
            "speed_up_collect": (config.SE_SPEED_UP_COLLECT_PATH, config.SE_ITEM_COLLECT_VOLUME),
            "size_up_collect": (config.SE_SIZE_UP_COLLECT_PATH, config.SE_ITEM_COLLECT_VOLUME),
            "gauge_max": (config.SE_GAUGE_MAX_PATH, config.SE_VOLUME),
        }

        # 音階SEを追加
        for i, path in enumerate(config.SCALE_SOUND_PATHS):
            key = f"scale_{i}"
            se_definitions[key] = (path, config.SE_VOLUME)

        # BGMはpygame.mixer.musicでストリーミング再生するため、ここでは読み込まない

        for key, (path, volume) in se_definitions.items():
            self.sounds_to_load.append((key, path, volume))

        self.total_assets = len(self.images_to_load) + len(self.sounds_to_load)
        print(f"AssetManager: {self.total_assets}個のアセットを読み込みます。")

    def load_next_asset(self):
        """
        アセットを1つ読み込む。Webブラウザをフリーズさせないため、1フレームに1つずつ処理する。
        :return: まだ読み込むべきアセットが残っていればTrue、すべて完了したらFalse
        """
        if self.loaded_assets >= self.total_assets:
            return False

        # 現在は音声のみ
        if self.loaded_assets < len(self.sounds_to_load):
            key, path, volume = self.sounds_to_load[self.loaded_assets]
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(volume)
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
        self.total_assets -= len(self.sounds_to_load)
        self.sounds_to_load.clear()
