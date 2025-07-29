# Copyright (c) 2025 [k3]
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pygame
import math
import random
import config
from bird import Bird
from cloud import Cloud
from ground import Ground
from enemy import Enemy
from tower import Tower
from heart_item import HeartItem
from flying_enemy import FlyingEnemy
from game_logic import GameLogicManager, calculate_trajectory
from ui import UIManager
from level_utils import create_cloud_layout

def setup_level(slingshot_x, tower_top_y):
    """
    ゲームのレベル（弾、ブロック、雲）をセットアップし、オブジェクトを返す。
    """
    # タワーのインスタンスを先に作成
    tower_base_x = slingshot_x - config.TOWER_BLOCK_WIDTH / 2
    tower = Tower(tower_base_x, config.GROUND_Y, tower_top_y)

    # 弾のインスタンスを作成
    # 弾の初期Y座標は、作成されたタワーの現在のてっぺんになる
    bird = Bird(slingshot_x, tower.get_top_y() + config.SLINGSHOT_OFFSET_Y, config.BIRD_DEFAULT_RADIUS)

    clouds = create_cloud_layout(slingshot_x, tower_top_y)

    # 地面のインスタンスを作成
    ground = Ground()

    # 敵リストを初期化
    enemies = []

    return bird, tower, clouds, ground, enemies

def reset_game(slingshot_x, initial_tower_top_y, ui_manager):
    """
    ゲームを初期化またはリセットし、すべてのオブジェクトとマネージャーを返す。
    """
    # レベルの基本オブジェクトをセットアップ
    (
        bird, tower, clouds, ground, enemies
    ) = setup_level(slingshot_x, initial_tower_top_y)

    # その他のオブジェクトリストを初期化
    heart_items = []
    particles = []

    # スリングショットの位置を計算
    slingshot_pos = pygame.math.Vector2(slingshot_x, tower.get_top_y() + config.SLINGSHOT_OFFSET_Y)

    # GameLogicManagerを初期化
    game_logic_manager = GameLogicManager(
        bird, tower, clouds, ground, enemies,
        heart_items, particles, slingshot_pos, ui_manager
    )

    # 生成したすべてのオブジェクトとマネージャーをタプルで返す
    return (
        bird, tower, clouds, ground, enemies,
        heart_items, particles, game_logic_manager, slingshot_pos
    )

def main():
    """ゲームのメインループ"""
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Babel's Tower Defense")
    clock = pygame.time.Clock()
    # フォントの準備
    ui_font = pygame.font.Font(None, 72) # UI用フォント
    title_font = pygame.font.Font(None, 120) # タイトル用フォント
    boss_font = pygame.font.Font(None, config.BOSS_NAME_FONT_SIZE) # ボス戦UI用フォント
    combo_font = pygame.font.Font(None, config.COMBO_TEXT_FONT_SIZE) # コンボ表示用フォント

    # UIマネージャーのインスタンスを作成
    ui_manager = UIManager(screen, ui_font, title_font, boss_font, combo_font)

    # スリングショットのX座標と、タワーの初期の高さを定義
    slingshot_x = config.SLINGSHOT_X
    initial_tower_top_y = config.GROUND_Y - (config.TOWER_INITIAL_BLOCKS * config.TOWER_BLOCK_HEIGHT)

    # --- ゲームオブジェクトのセットアップ ---
    # reset_game関数を呼び出して、すべてのオブジェクトとマネージャーを一度に受け取る
    (
        bird, tower, clouds, ground, enemies,
        heart_items, particles, game_logic_manager, slingshot_pos
    ) = reset_game(slingshot_x, initial_tower_top_y, ui_manager)

    # --- ゲームループ用変数 ---
    is_dragging = False
    trajectory_points = [] # 軌道の点を保持するリスト
    mouse_pos = pygame.math.Vector2(0, 0) # マウスカーソルの位置を保持
    recall_button_rect = None # 呼び戻しボタンのRectを保持する変数

    running = True

    while running:
        # --- イベント処理 (Input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # キーボード入力
            if event.type == pygame.KEYDOWN:
                # デバッグモードがTrueの時だけ、'ESC'キーでレベル全体をリスタート
                if event.key == pygame.K_r:
                    # ゲームオーバー/ゲームクリア時、またはデバッグモードが有効な時にリスタート
                    if game_logic_manager.stage_state in ["GAME_OVER", "GAME_WON"] or config.DEBUG:
                        # reset_gameを呼び出して、すべてのオブジェクトとマネージャーを再生成
                        (
                            bird, tower, clouds, ground, enemies,
                            heart_items, particles, game_logic_manager, slingshot_pos
                        ) = reset_game(slingshot_x, initial_tower_top_y, ui_manager)
                        is_dragging = False
                        trajectory_points.clear()
                        print("--- Level Restarted ---")
                
                # --- デバッグ用ステージセレクト ---
                if config.DEBUG:
                    # 数字キー (1-9) でステージジャンプ
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        stage_num = event.key - pygame.K_0
                        game_logic_manager.jump_to_stage(stage_num)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 呼び戻しボタンが押されたかチェック
                if recall_button_rect and recall_button_rect.collidepoint(event.pos):
                    bird.reset(slingshot_pos)
                    game_logic_manager.is_bird_callable = False # 即座にフラグを折る
                    print("Bird recalled manually.")

            # マウス入力
            if not bird.is_flying and game_logic_manager.stage_state == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and bird.is_clicked(event.pos):
                        is_dragging = True
                        # ドラッグ開始時に、現在のマウス位置を同期させる
                        mouse_pos.x, mouse_pos.y = event.pos
                
                if event.type == pygame.MOUSEMOTION:
                    if is_dragging:
                        # マウスの位置を更新するだけにする
                        mouse_pos.x, mouse_pos.y = event.pos

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and is_dragging:
                        is_dragging = False
                        # 発射ベクトルを計算（スリングショットの位置 - 離した位置）
                        launch_vector = slingshot_pos - bird.pos
                        bird.launch(launch_vector)
                        trajectory_points.clear() # 発射したら軌道を消す

        # --- 状態更新 (Update) ---
        # タワーの高さに応じてスリングショットのY座標を更新
        slingshot_pos.y = tower.get_top_y() + config.SLINGSHOT_OFFSET_Y

        # 弾の状態に応じて位置を更新
        if is_dragging:
            # ドラッグ中は、スリングショットの位置が変化した場合に備えて、
            # 弾の位置をマウスカーソルに追従させ、引き伸ばし範囲内に制限する
            bird.pos = mouse_pos.copy()

            # 弾の位置を引き伸ばし範囲内に再制限する。
            # (マウスイベントがないフレームでも追従させるため)
            distance = slingshot_pos.distance_to(bird.pos)
            if distance > config.MAX_PULL_DISTANCE:
                # bird.posがslingshot_posと完全に一致するとnormalize()でエラーになるため、チェックを追加
                if distance > 0:
                    direction = (bird.pos - slingshot_pos).normalize()
                    bird.pos = slingshot_pos + direction * config.MAX_PULL_DISTANCE
                else: # 完全に一致している場合（通常は起こらないが念のため）
                    bird.pos = slingshot_pos.copy()

        elif bird.is_flying:
            # 飛行中は物理演算を適用
            bird.update()
        else: # アイドル状態
            # 弾の位置を常に最新のスリングショットの位置に合わせる
            bird.pos = slingshot_pos.copy()
            bird.start_pos = slingshot_pos.copy()

        # 各ゲームオブジェクトの更新
        for cloud in clouds:
            cloud.update()
        for heart in heart_items:
            heart.update()
        for p in particles:
            p.update()
        for enemy in enemies: # 敵の種類によって渡す引数を変更
            if isinstance(enemy, FlyingEnemy):
                enemy.update(tower)
            else: # Enemy, BossEnemy
                enemy.update(tower, ground)

        tower.update()
        ground.update()

        # ゲームロジック全体（衝突、生成、状態遷移など）を更新
        game_logic_manager.update()

        # ドラッグ中であれば、現在の位置から軌道を計算する
        if is_dragging:
            current_launch_vector = slingshot_pos - bird.pos
            trajectory_points = calculate_trajectory(bird.pos, current_launch_vector)

        # --- 描画処理 (Draw) ---
        screen.fill(config.BLUE) # 背景を青空の色に

        # 雲を描画 (他のオブジェクトより先に描画して背景にする)
        for cloud in clouds:
            cloud.draw(screen)

        # 地面を描画
        ground.draw(screen)

        # 敵を描画
        for enemy in enemies:
            enemy.draw(screen)

        # タワーを描画
        tower.draw(screen)

        # ハートアイテムを描画
        for heart in heart_items:
            heart.draw(screen)

        # パーティクルを描画
        for p in particles:
            p.draw(screen)

        # 軌道ガイドを描画 (ドラッグ中のみ)
        if is_dragging:
            for point in trajectory_points:
                pygame.draw.circle(screen, config.WHITE, (int(point.x), int(point.y)), config.TRAJECTORY_POINT_RADIUS)

        # スリングショットの支柱を描画
        post_rect = pygame.Rect(
            slingshot_pos.x - config.SLINGSHOT_POST_WIDTH / 2,
            slingshot_pos.y, # 支柱の上端をスリングショットの基点に合わせる
            config.SLINGSHOT_POST_WIDTH,
            config.SLINGSHOT_POST_HEIGHT
        )
        pygame.draw.rect(screen, config.SLINGSHOT_POST_COLOR, post_rect)
        pygame.draw.rect(screen, config.BLACK, post_rect, 2) # 枠線

        # スリングショットのゴムを描画
        if is_dragging:
            pygame.draw.line(screen, config.BLACK, slingshot_pos, bird.pos, 5)
        
        # 呼び戻しボタンを描画
        if game_logic_manager.is_bird_callable:
            # 発射台の少し上にボタンを表示
            button_pos = slingshot_pos - pygame.math.Vector2(0, config.RECALL_BUTTON_OFFSET_Y)
            recall_button_rect = ui_manager.draw_recall_button(button_pos)
        else:
            recall_button_rect = None

        # 弾を描画
        bird.draw(screen)

        # --- UIの描画 ---
        # UIManagerを使ってHUD（ライフ、カウンター）を描画
        settings = game_logic_manager.stage_manager.get_current_stage_settings()
        enemies_to_clear = settings["clear_enemies_count"] if settings else 0
        boss = game_logic_manager.current_boss
        boss_name = settings.get("boss_name") if settings else None
        ui_manager.draw_game_hud(
            tower, 
            game_logic_manager.enemies_defeated_count,
            enemies_to_clear,
            game_logic_manager.stage_manager.current_stage,
            boss=boss,
            boss_name=boss_name
        )

        # UIManagerを使ってゲームオーバー/クリア画面を描画
        if game_logic_manager.stage_state != "PLAYING":
            ui_manager.draw_end_screen(game_logic_manager.stage_state)

        # コンボ表示など、すべてのUIの上に描画する要素
        ui_manager.draw_ui_overlays()

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
