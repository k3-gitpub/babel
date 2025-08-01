import pygame
import config
import os

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
        # BGMファイルが存在するかどうかを事前にチェック
        self.music_loaded = {
            "normal": os.path.exists(config.BGM_NORMAL_PATH),
            "boss": os.path.exists(config.BGM_BOSS_PATH),
        }
        if not any(self.music_loaded.values()):
            print("警告: BGMファイルが一つも見つかりません。BGMは再生されません。")
        
        # --- コンボヒットSEの読み込み ---
        self.combo_hit_sound = None
        if os.path.exists(config.SE_COMBO_HIT_PATH):
            self.combo_hit_sound = pygame.mixer.Sound(config.SE_COMBO_HIT_PATH)
            self.combo_hit_sound.set_volume(config.SE_COMBO_HIT_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_COMBO_HIT_PATH}")

        # --- SEの初期化 ---
        self.scale_sounds = []
        sounds_found = 0
        for path in config.SCALE_SOUND_PATHS:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(config.SE_VOLUME)
                self.scale_sounds.append(sound)
                sounds_found += 1
            else:
                print(f"警告: SEファイルが見つかりません: {path}")
        
        # 読み込めたSEが一つもなければ、リストを空にして警告を出す
        if sounds_found == 0:
            self.scale_sounds.clear() # 念のためクリア
            print("音階SEは再生されません。")

        # 敵死亡SEの読み込み
        self.enemy_death_sound = None
        if os.path.exists(config.SE_ENEMY_DEATH_PATH):
            self.enemy_death_sound = pygame.mixer.Sound(config.SE_ENEMY_DEATH_PATH)
            self.enemy_death_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_ENEMY_DEATH_PATH}")

        # 敵ヒットSEの読み込み
        self.enemy_hit_sound = None
        if os.path.exists(config.SE_ENEMY_HIT_PATH):
            self.enemy_hit_sound = pygame.mixer.Sound(config.SE_ENEMY_HIT_PATH)
            self.enemy_hit_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_ENEMY_HIT_PATH}")

        # タワーダメージSEの読み込み
        self.tower_damage_sound = None
        if os.path.exists(config.SE_TOWER_DAMAGE_PATH):
            self.tower_damage_sound = pygame.mixer.Sound(config.SE_TOWER_DAMAGE_PATH)
            self.tower_damage_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_TOWER_DAMAGE_PATH}")

        # ハート取得SEの読み込み
        self.heart_collect_sound = None
        if os.path.exists(config.SE_HEART_COLLECT_PATH):
            self.heart_collect_sound = pygame.mixer.Sound(config.SE_HEART_COLLECT_PATH)
            self.heart_collect_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_HEART_COLLECT_PATH}")

        # ステージ開始SEの読み込み
        self.stage_start_sound = None
        if os.path.exists(config.SE_STAGE_START_PATH):
            self.stage_start_sound = pygame.mixer.Sound(config.SE_STAGE_START_PATH)
            self.stage_start_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_STAGE_START_PATH}")

        # UIクリックSEの読み込み
        self.ui_click_sound = None
        if os.path.exists(config.SE_UI_CLICK_PATH):
            self.ui_click_sound = pygame.mixer.Sound(config.SE_UI_CLICK_PATH)
            self.ui_click_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_UI_CLICK_PATH}")

        # アイテム出現SEの読み込み
        self.item_spawn_sound = None
        if os.path.exists(config.SE_ITEM_SPAWN_PATH):
            self.item_spawn_sound = pygame.mixer.Sound(config.SE_ITEM_SPAWN_PATH)
            self.item_spawn_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_ITEM_SPAWN_PATH}")

        # スピードアップ取得SEの読み込み
        self.speed_up_collect_sound = None
        if os.path.exists(config.SE_SPEED_UP_COLLECT_PATH):
            self.speed_up_collect_sound = pygame.mixer.Sound(config.SE_SPEED_UP_COLLECT_PATH)
            self.speed_up_collect_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_SPEED_UP_COLLECT_PATH}")

        # 巨大化取得SEの読み込み
        self.size_up_collect_sound = None
        if os.path.exists(config.SE_SIZE_UP_COLLECT_PATH):
            self.size_up_collect_sound = pygame.mixer.Sound(config.SE_SIZE_UP_COLLECT_PATH)
            self.size_up_collect_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_SIZE_UP_COLLECT_PATH}")

        # ゲージ満タンSEの読み込み
        self.gauge_max_sound = None
        if os.path.exists(config.SE_GAUGE_MAX_PATH):
            self.gauge_max_sound = pygame.mixer.Sound(config.SE_GAUGE_MAX_PATH)
            self.gauge_max_sound.set_volume(config.SE_VOLUME)
        else:
            print(f"警告: SEファイルが見つかりません: {config.SE_GAUGE_MAX_PATH}")

        pygame.mixer.music.set_volume(config.BGM_VOLUME)
        self.scale_index = 0

    def toggle_enabled(self):
        """サウンドの有効/無効を切り替える。"""
        self.enabled = not self.enabled
        print(f"Sound enabled: {self.enabled}")
        # サウンドが無効になったら、再生中のBGMを止める
        if not self.enabled:
            self.stop_music()

    def _play_music(self, bgm_type: str):
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
            if self.combo_hit_sound:
                self.combo_hit_sound.play()

    def play_scale_sound(self):
        """現在の音階のSEを再生し、次の音階に進める。"""
        if not self.enabled or not self.scale_sounds:
            return

        # 現在のインデックスのサウンドを再生
        sound_to_play = self.scale_sounds[self.scale_index]
        sound_to_play.play()

        # インデックスを次に進める (リストの範囲でループ)
        self.scale_index = (self.scale_index + 1) % len(self.scale_sounds)

    def play_enemy_death_sound(self):
        """敵の死亡SEを再生する。"""
        if self.enabled and self.enemy_death_sound:
            self.enemy_death_sound.play()

    def play_enemy_hit_sound(self):
        """敵ヒットSEを再生する。"""
        if self.enabled and self.enemy_hit_sound:
            self.enemy_hit_sound.play()

    def play_tower_damage_sound(self):
        """タワーのダメージSEを再生する。"""
        if self.enabled and self.tower_damage_sound:
            self.tower_damage_sound.play()

    def play_heart_collect_sound(self):
        """ハート取得SEを再生する。"""
        if self.enabled and self.heart_collect_sound:
            self.heart_collect_sound.play()

    def play_stage_start_sound(self):
        """ステージ開始SEを再生する。"""
        if self.enabled and self.stage_start_sound:
            self.stage_start_sound.play()

    def play_ui_click_sound(self):
        """UIクリックSEを再生する。"""
        if self.enabled and self.ui_click_sound:
            self.ui_click_sound.play()

    def play_item_spawn_sound(self):
        """アイテム出現SEを再生する。"""
        if self.enabled and self.item_spawn_sound:
            self.item_spawn_sound.play()

    def play_speed_up_collect_sound(self):
        """スピードアップ取得SEを再生する。"""
        if self.enabled and self.speed_up_collect_sound:
            self.speed_up_collect_sound.play()

    def play_size_up_collect_sound(self):
        """巨大化取得SEを再生する。"""
        if self.enabled and self.size_up_collect_sound:
            self.size_up_collect_sound.play()

    def play_gauge_max_sound(self):
        """ゲージ満タンSEを再生する。"""
        if self.enabled and self.gauge_max_sound:
            self.gauge_max_sound.play()

    def reset_scale(self):
        """音階を最初（ド）に戻す。"""
        if self.scale_index != 0:
            print("音階をリセットします。")
            self.scale_index = 0

    def update(self, game_state: str, is_boss_stage: bool):
        """
        ゲームの状態に応じてBGMを更新する。
        :param game_state: 現在のゲーム状態 ("TITLE", "PLAYING"など)
        :param is_boss_stage: 現在がボスステージかどうか
        """
        if game_state == "PLAYING":
            if is_boss_stage:
                self._play_music("boss")
            else:
                self._play_music("normal")
        else: # TITLE, GAME_OVER, GAME_WONなどの状態
            self.stop_music()