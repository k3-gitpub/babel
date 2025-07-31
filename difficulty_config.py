# difficulty_config.py

"""
各ステージの難易度設定を定義するファイル。
このファイルを編集することで、ゲームバランスを調整できます。
"""

STAGES = {
    1: {
        "stage_name": "平穏な丘",
        "clear_enemies_count": 5,
        "enemy_spawn_interval": 5000,  # ミリ秒
        "enemy_weights": {"ground": 80, "flying": 20}, # 地上敵: 80%, 飛行敵: 20%
        "stat_multiplier": {"hp": 1.0, "speed": 1.0, "attack": 1.0},
        "heart_spawn": {"base": 10000, "random": 2000}, # 15秒 ± 5秒
        "is_boss_stage": False,
        "boss_type": None,
        "rearrange_clouds": True, # 雲の再配置
    },
    2: {
        "stage_name": "風の谷",
        "clear_enemies_count": 10,
        "enemy_spawn_interval": 4500,
        "enemy_weights": {"ground": 50, "flying": 50, "jumping": 0},
        "stat_multiplier": {"hp": 1.2, "speed": 1.2, "attack": 1.2},
        "heart_spawn": {"base": 15000, "random": 2000}, # 20秒 ± 5秒
        "is_boss_stage": False,
        "boss_type": None,
        "rearrange_clouds": True, # 雲の再配置
    },
    3: {
        "stage_name": "巨人の寝床",
        "boss_name": "3 EYED ANGEL", # ボスの名前
        "clear_enemies_count": 1, # ボスを1体倒せばクリア
        "enemy_spawn_interval": 6000, # ボス戦中はザコ敵が時々出現する
        "enemy_weights": {"ground": 60, "flying": 40}, 
        "stat_multiplier": {"hp": 1.0, "speed": 1.0, "attack": 1.0}, # ボス固有のステータスを使うので補正は1.0
        "heart_spawn": {"base": 20000, "random": 2000}, # 25秒 ± 8秒
        "is_boss_stage": True,
        "boss_type": "giant_square", # 後で実装するボスの種類
        "rearrange_clouds": True, # 雲の再配置
    },
        4: {
        "stage_name": "",
        "clear_enemies_count": 10,
        "enemy_spawn_interval": 4000,  # ミリ秒
        "enemy_weights": {"ground": 30, "flying": 40, "jumping": 30},
        "stat_multiplier": {"hp": 1.2, "speed": 1.2, "attack": 1.2},
        "heart_spawn": {"base": 10000, "random": 5000}, # 15秒 ± 5秒
        "is_boss_stage": False,
        "boss_type": None,
        "rearrange_clouds": True, # 雲の再配置
    },
        5: {
        "stage_name": "",
        "clear_enemies_count": 20,
        "enemy_spawn_interval": 3500,  # ミリ秒
        "enemy_weights": {"ground": 20, "flying": 30, "jumping": 50},
        "stat_multiplier": {"hp": 1.2, "speed": 1.2, "attack": 1.2},
        "heart_spawn": {"base": 15000, "random": 5000}, # 15秒 ± 5秒
        "is_boss_stage": False,
        "boss_type": None,
        "rearrange_clouds": True, # 雲の再配置
    },
        6: {
        "stage_name": "巨人の寝床",
        "boss_name": "3 EYED ANGEL2", # ボスの名前
        "clear_enemies_count": 1, # ボスを1体倒せばクリア
        "enemy_spawn_interval": 4000, # ボス戦中はザコ敵が時々出現する
        "enemy_weights": {"ground": 30, "flying": 30, "jumping": 40}, 
        "stat_multiplier": {"hp": 1.2, "speed": 1.2, "attack": 1.2}, # ボス固有のステータスを使うので補正は1.0
        "heart_spawn": {"base": 20000, "random": 2000}, # 25秒 ± 8秒
        "is_boss_stage": True,
        "boss_type": "giant_square", # 後で実装するボスの種類
        "rearrange_clouds": True, # 雲の再配置
    },
    # 今後、ステージ4, 5, 6...と追加していく
}