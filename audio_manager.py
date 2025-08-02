import pygame
import config
import os
from typing import Dict, Tuple, List, Optional

class AudioManager:
    """
    BGMの再生、切り替え、停止を管理するクラス。
    """
    def __init__(self, initial_enabled=True):
        """AudioManagerを初期化する。"""
        self.enabled = initial_enabled # サウンドが有効かどうかのフラグ
        self.current_bgm_type = None
        self.bgm_paths = {
            "normal": config.BGM_NORMAL_PATH,
            "boss": config.BGM_BOSS_PATH,
        }
        self.se_paths: Dict[str, Tuple[str, float]] = {
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
        self.sound_cache: Dict[str, Optional[pygame.mixer.Sound]] = {}

        # BGMファイルが存在するかどうかを事前にチェック
        self.music_loaded = {
            "normal": os.path.exists(config.BGM_NORMAL_PATH),
            "boss": os.path.exists(config.BGM_BOSS_PATH),
        }
        if not any(self.music_loaded.values()):
            print("警告: BGMファイルが一つも見つかりません。BGMは再生されません。")

        # --- 音階SEのキーを順番に定義 ---
        self.scale_sound_keys = [f"scale_{i}" for i in range(len(config.SCALE_SOUND_PATHS))]
        for i, path in enumerate(config.SCALE_SOUND_PATHS):
            key = self.scale_sound_keys[i]
            self.se_paths[key] = (path, config.SE_VOLUME)

        pygame.mixer.music.set_volume(config.BGM_VOLUME)
        self.scale_index = 0

    def _load_and_play_sound(self, key: str):
        """
        指定されたキーの効果音をキャッシュから探すか、必要なら読み込んで再生する。
        :param key: self.se_paths に定義されている効果音のキー
        """
        if not self.enabled:
            return

        # 1. キャッシュを確認
        if key in self.sound_cache:
            sound = self.sound_cache[key]
            if sound:
                sound.play()
            return

        # 2. キャッシュになければ、パスを取得して読み込みを試みる
        if key in self.se_paths:
            path, volume = self.se_paths[key]
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(volume)
                    self.sound_cache[key] = sound
                    sound.play()
                except pygame.error as e:
                    print(f"エラー: SEファイル '{path}' の読み込みに失敗しました: {e}")
                    self.sound_cache[key] = None # 読み込み失敗を記録
            else:
                print(f"警告: SEファイルが見つかりません: {path}")
                self.sound_cache[key] = None # ファイルなしを記録

    def toggle_enabled(self):
        """サウンドの有効/無効を切り替える。"""
        self.enabled = not self.enabled
        print(f"Sound enabled: {self.enabled}")
        # サウンドが無効になったら、再生中のBGMを止める
        if not self.enabled:
            self.stop_music()

    def play_bgm(self, bgm_type: str):
        """
        指定されたタイプのBGMを再生する。
        :param bgm_type: "normal" または "boss"
        """
        # サウンドが無効な場合は再生しない
        if not self.enabled:
            return
        # すでに同じBGMが再生中、またはファイルが存在しない場合は何もしない
        if self.current_bgm_type == bgm_type:
            return
        # 再生しようとしているBGMファイルが存在しない場合は、現在のBGMを止めずに処理を中断
        if not self.music_loaded.get(bgm_type, False):
            return

        print(f"BGMを '{self.current_bgm_type}' から '{bgm_type}' に切り替えます。")
        pygame.mixer.music.fadeout(config.BGM_FADEOUT_MS)
        pygame.mixer.music.load(self.bgm_paths[bgm_type])
        pygame.mixer.music.play(-1, fade_ms=1000) # -1でループ再生、1秒でフェードイン
        self.current_bgm_type = bgm_type

    def stop_music(self):
        """BGMをフェードアウトしながら停止する。"""
        if self.current_bgm_type is not None:
            print("BGMを停止します。")
            pygame.mixer.music.fadeout(config.BGM_FADEOUT_MS)
            self.current_bgm_type = None

    def play_combo_sound(self):
        """
        コンボヒット音を再生する。設定に応じて音階SEか単一SEかを切り替える。
        """
        if not self.enabled:
            return

        if config.USE_SCALE_SOUND_FOR_COMBO:
            self.play_scale_sound()
        else:
            self._load_and_play_sound("combo_hit")

    def play_scale_sound(self):
        """現在の音階のSEを再生し、次の音階に進める。"""
        if not self.enabled or not self.scale_sound_keys:
            return

        # 現在のインデックスに対応するキーを取得
        key_to_play = self.scale_sound_keys[self.scale_index]
        self._load_and_play_sound(key_to_play)

        # インデックスを次に進める (リストの範囲でループ)
        self.scale_index = (self.scale_index + 1) % len(self.scale_sound_keys)

    def play_enemy_death_sound(self):
        """敵の死亡SEを再生する。"""
        self._load_and_play_sound("enemy_death")

    def play_enemy_hit_sound(self):
        """敵ヒットSEを再生する。"""
        self._load_and_play_sound("enemy_hit")

    def play_tower_damage_sound(self):
        """タワーのダメージSEを再生する。"""
        self._load_and_play_sound("tower_damage")

    def play_heart_collect_sound(self):
        """ハート取得SEを再生する。"""
        self._load_and_play_sound("heart_collect")

    def play_stage_start_sound(self):
        """ステージ開始SEを再生する。"""
        self._load_and_play_sound("stage_start")

    def play_ui_click_sound(self):
        """UIクリックSEを再生する。"""
        self._load_and_play_sound("ui_click")

    def play_item_spawn_sound(self):
        """アイテム出現SEを再生する。"""
        self._load_and_play_sound("item_spawn")

    def play_speed_up_collect_sound(self):
        """スピードアップ取得SEを再生する。"""
        self._load_and_play_sound("speed_up_collect")

    def play_size_up_collect_sound(self):
        """巨大化取得SEを再生する。"""
        self._load_and_play_sound("size_up_collect")

    def play_gauge_max_sound(self):
        """ゲージ満タンSEを再生する。"""
        self._load_and_play_sound("gauge_max")

    def reset_scale(self):
        """音階を最初（ド）に戻す。"""
        if self.scale_index != 0:
            print("音階をリセットします。")
            self.scale_index = 0