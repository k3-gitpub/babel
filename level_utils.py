import pygame
import random
import config
from cloud import Cloud

def create_cloud_layout(slingshot_x, tower_top_y, min_count=config.CLOUD_MIN_COUNT, max_count=config.CLOUD_MAX_COUNT):
    """
    重ならないように雲を生成し、リストとして返す。
    最低個数を下回った場合は、生成をやり直す。
    :param min_count: 生成する雲の最小数
    :param max_count: 生成する雲の最大数
    """
    outer_attempts = 0
    max_outer_attempts = 10 # 生成全体のリトライ回数

    while outer_attempts < max_outer_attempts:
        clouds = []
        num_clouds = random.randint(min_count, max_count)
        max_attempts = 100 # 無限ループを避けるための最大試行回数
        attempts = 0

        while len(clouds) < num_clouds and attempts < max_attempts:
            # 画面の端からパディングを考慮した範囲でランダムな位置を生成
            cloud_x = random.randint(
                config.CLOUD_SPAWN_PADDING_X,
                config.SCREEN_WIDTH - config.CLOUD_SPAWN_PADDING_X
            )
            cloud_y = random.randint(
                config.CLOUD_SPAWN_Y_MIN,
                config.CLOUD_SPAWN_Y_MAX
            )
            new_cloud_pos = pygame.math.Vector2(cloud_x, cloud_y)

            # 他の雲と近すぎないかチェック (X, Y個別の矩形判定)
            is_too_close_to_clouds = any(
                (abs(new_cloud_pos.x - c.center.x) < config.CLOUD_MIN_DISTANCE_X and
                 abs(new_cloud_pos.y - c.center.y) < config.CLOUD_MIN_DISTANCE_Y)
                for c in clouds)

            # 塔と近すぎないかチェック（円範囲で判定）
            initial_slingshot_pos = pygame.math.Vector2(slingshot_x, tower_top_y)
            is_too_close_to_tower = new_cloud_pos.distance_to(initial_slingshot_pos) < config.CLOUD_MIN_DISTANCE_FROM_TOWER

            # 位置が問題なければ雲を生成してリストに追加
            if not is_too_close_to_clouds and not is_too_close_to_tower:
                num_puffs = random.randint(3, 5)
                clouds.append(Cloud(cloud_x, cloud_y, num_puffs))

            attempts += 1

        # 生成された雲の数が最低個数を満たしていれば、ループを抜けて結果を返す
        if len(clouds) >= min_count:
            print(f"雲の生成に成功しました。個数: {len(clouds)}")
            return clouds
        
        outer_attempts += 1
        print(f"雲の生成数が最低個数({min_count})に満たなかったため、リトライします... ({outer_attempts}/{max_outer_attempts})")

    # 最大リトライ回数に達しても最低個数を満たせなかった場合
    print(f"警告: 雲の生成に失敗しました。最後に生成された不完全な雲のリストを返します。個数: {len(clouds)}")
    return clouds # 最後に生成された（不完全な）雲のリストを返す