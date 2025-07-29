import pygame
import random
import config
from cloud import Cloud

def create_cloud_layout(slingshot_x, tower_top_y):
    """
    重ならないように雲を生成し、リストとして返す。
    """
    # --- 雲の生成（重ならないように配置） ---
    clouds = []
    num_clouds = random.randint(4, 7)
    max_attempts = 50 # 無限ループを避けるための最大試行回数
    attempts = 0

    while len(clouds) < num_clouds and attempts < max_attempts:
        # 画面の端からパディングを考慮した範囲でランダムな位置を生成
        cloud_x = random.randint(
            config.CLOUD_SPAWN_PADDING_X,
            config.SCREEN_WIDTH - config.CLOUD_SPAWN_PADDING_X
        )
        cloud_y = random.randint(
            config.CLOUD_SPAWN_PADDING_Y,
            config.CLOUD_SPAWN_Y_MAX # Y座標の下限を設定ファイルから読み込む
        )
        new_cloud_pos = pygame.math.Vector2(cloud_x, cloud_y)

        # 他の雲と近すぎないかチェック
        is_too_close_to_clouds = any(new_cloud_pos.distance_to(c.center) < config.CLOUD_MIN_DISTANCE for c in clouds)

        # 塔と近すぎないかチェック（円範囲で判定）
        initial_slingshot_pos = pygame.math.Vector2(slingshot_x, tower_top_y)
        is_too_close_to_tower = new_cloud_pos.distance_to(initial_slingshot_pos) < config.CLOUD_MIN_DISTANCE_FROM_TOWER

        # 位置が問題なければ雲を生成してリストに追加
        if not is_too_close_to_clouds and not is_too_close_to_tower:
            num_puffs = random.randint(3, 7)
            clouds.append(Cloud(cloud_x, cloud_y, num_puffs))

        attempts += 1
    return clouds