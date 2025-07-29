import pygame
import random
import config
from enemy import Enemy
from flying_enemy import FlyingEnemy
from heart_item import HeartItem
from particle import Particle
from stage_manager import StageManager
from boss_enemy import BossEnemy
from cloud import Cloud
from level_utils import create_cloud_layout

def calculate_trajectory(start_pos, launch_vector):
    """
    与えられた初期位置と発射ベクトルから、弾の軌道を予測して点のリストを返す。
    :param start_pos: 軌道計算の開始位置 (Vector2)
    :param launch_vector: 発射ベクトル (Vector2)
    :return: 軌道上の点のリスト [Vector2, Vector2, ...]
    """
    points = []
    # 実際の物理演算と同じパラメータで計算
    velocity = launch_vector * config.LAUNCH_POWER_MULTIPLIER
    pos = start_pos.copy()
    
    # 物理シミュレーションのステップ数
    # 1ステップが1フレームに相当すると考え、指定した数の点を計算する
    num_steps = config.TRAJECTORY_NUM_POINTS * config.TRAJECTORY_POINT_GAP
    for step in range(1, num_steps + 1):
        velocity.y += config.GRAVITY
        pos += velocity
        # 指定した間隔ごとに点をリストに追加
        if step % config.TRAJECTORY_POINT_GAP == 0:
            points.append(pos.copy())
    return points

class GameLogicManager:
    """
    ゲームのロジック（衝突判定、エンティティ生成、状態遷移など）を管理するクラス。
    """
    def __init__(self, bird, tower, clouds, ground, enemies, heart_items, particles, slingshot_pos, ui_manager):
        # ゲームオブジェクトへの参照を保持
        self.bird = bird
        self.tower = tower
        self.clouds = clouds
        self.ground = ground
        self.enemies = enemies
        self.heart_items = heart_items
        self.particles = particles
        self.slingshot_pos = slingshot_pos
        self.ui_manager = ui_manager

        # ステージ管理クラスを初期化
        self.stage_manager = StageManager()

        # ゲームの状態とタイマーを初期化
        self.reset_level_state()

        # ボスが出現したかどうかを追跡するフラグ
        self.boss_spawned = False

        # 弾の呼び戻し機能に関する状態
        self.is_bird_callable = False
        self.bird_last_active_time = pygame.time.get_ticks()

    def update(self):
        """ゲームロジック全体を更新する。メインループから毎フレーム呼ばれる。"""
        self._check_game_over()

        if self.stage_state == "PLAYING":
            self._spawn_entities()
            self._handle_collisions()
            self._check_bird_reset()
            self._check_stage_clear()
            self._check_bird_callable()
        elif self.stage_state == "CLEARING":
            # ステージクリア後の待機処理
            if not hasattr(self, 'stage_clear_time'):
                self.stage_clear_time = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - self.stage_clear_time > config.STAGE_CLEAR_WAIT_TIME:
                self._transition_to_next_stage()
                # タイマーを削除。次のステージクリアまで不要。
                if hasattr(self, 'stage_clear_time'):
                    del self.stage_clear_time

        self._cleanup_entities()

    def reset_level_state(self):
        """ゲームの状態を現在のステージ開始時にリセットする。"""
        self.stage_state = "PLAYING"
        self.enemies_defeated_count = 0
        self.boss_spawned = False

        # 現在のステージ設定に基づいてタイマーをリセット
        settings = self.stage_manager.get_current_stage_settings()
        spawn_interval = settings.get("enemy_spawn_interval", config.ENEMY_SPAWN_INTERVAL)

        self.last_enemy_spawn_time = pygame.time.get_ticks() - (spawn_interval - config.FIRST_ENEMY_SPAWN_DELAY)
        self.next_heart_spawn_time = self._calculate_next_heart_spawn_time(pygame.time.get_ticks())

    def _check_game_over(self):
        """ゲームオーバー条件をチェックする。"""
        if self.tower.is_destroyed() and self.stage_state == "PLAYING":
            self.stage_state = "GAME_OVER"
            print("ゲームオーバー！タワーが完全に破壊された。")

    def _check_stage_clear(self):
        """ステージクリア条件をチェックする。"""
        settings = self.stage_manager.get_current_stage_settings()
        if not settings:
            return

        if settings.get("is_boss_stage"):
            # --- ボスステージのクリア条件 ---
            # ボスが出現済みで、かつリスト内にボスが見つからない（倒された）場合にクリア
            boss_exists = any(isinstance(enemy, BossEnemy) for enemy in self.enemies)
            if self.boss_spawned and not boss_exists:
                self.stage_state = "CLEARING"
                print(f"ボスを撃破！ステージクリア！ ({self.stage_manager.current_stage})")
                # ボス撃破時に残りのザコ敵を全滅させる
                for enemy in self.enemies:
                    if not isinstance(enemy, BossEnemy):
                        enemy.destroy()
        else:
            # --- 通常ステージのクリア条件 ---
            if self.enemies_defeated_count >= settings["clear_enemies_count"]:
                self.stage_state = "CLEARING"
                print(f"ステージクリア！ ({self.stage_manager.current_stage}) 残りの敵を掃討します。")
                # 画面上の残りの敵を全滅させる
                for enemy in self.enemies:
                    enemy.destroy()

    def _spawn_entities(self):
        """敵やハートアイテムを時間経過で出現させる。"""
        current_time = pygame.time.get_ticks()
        settings = self.stage_manager.get_current_stage_settings()
        if not settings:
            return # 設定がなければ何もしない

        # ステージ設定からステータス補正値を取得
        stat_multiplier = settings.get("stat_multiplier", {"hp": 1.0, "speed": 1.0, "attack": 1.0})

        # --- ボスステージの特別処理 ---
        if settings.get("is_boss_stage") and not self.boss_spawned:
            # ボスを一度だけ出現させる
            if settings.get("boss_type") == "giant_square":
                self.enemies.append(BossEnemy(stat_multiplier))
                self.boss_spawned = True

        # ハートアイテムの出現処理 (動的・ランダム間隔)
        if current_time >= self.next_heart_spawn_time:
            if self.clouds:
                chosen_cloud = random.choice(self.clouds)
                self.heart_items.append(HeartItem(chosen_cloud))
                # 次の出現時間を計算してセット
                self.next_heart_spawn_time = self._calculate_next_heart_spawn_time(current_time)
                print(f"ハートアイテムが出現！ 次回出現まで約{((self.next_heart_spawn_time - current_time)/1000):.1f}秒")

        # 敵の出現間隔をステージ設定から取得
        enemy_spawn_interval = settings.get("enemy_spawn_interval", config.ENEMY_SPAWN_INTERVAL)
        # 敵の出現処理
        if current_time - self.last_enemy_spawn_time > enemy_spawn_interval:
            # タイマーを更新
            self.last_enemy_spawn_time = current_time

            enemy_weights = settings.get("enemy_weights")
            # 重みが設定されていない、または空の場合は敵を出現させない（ボスステージなどを想定）
            if not enemy_weights:
                return

            enemy_types = list(enemy_weights.keys())
            weights = list(enemy_weights.values())
            
            # 重みに基づいて敵の種類を決定
            chosen_enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]

            if chosen_enemy_type == "flying":
                spawn_x = config.SCREEN_WIDTH + config.FLYING_ENEMY_MAX_SIZE / 2
                spawn_y = random.uniform(config.FLYING_ENEMY_MIN_Y, config.FLYING_ENEMY_MAX_Y)
                self.enemies.append(FlyingEnemy(spawn_x, spawn_y, stat_multiplier))
                print("飛行する敵が出現！")
            elif chosen_enemy_type == "ground":
                self.enemies.append(Enemy(stat_multiplier))
                print("地上の敵が出現！")

    def _handle_collisions(self):
        """全ての衝突判定を処理する。"""
        self._handle_enemy_tower_collision()
        if self.bird.is_flying:
            self._handle_bird_cloud_collision()
            self._handle_bird_tower_collision()
            self._handle_bird_heart_collision()
            self._handle_bird_enemy_collision()
            self._handle_bird_ground_collision()

    def _handle_enemy_tower_collision(self):
        for enemy in self.enemies:
            if enemy.state != "DYING" and not enemy.velocity.length_squared() > 0.1:
                for block in self.tower.blocks:
                    if enemy.rect.colliderect(block.rect):
                        # --- ボスの場合、弱点との衝突か判定 ---
                        is_weak_point_hit_by_tower = False
                        if isinstance(enemy, BossEnemy):
                            for wp in enemy.weak_points:
                                # 弱点がアクティブで、かつブロックと衝突しているか
                                if wp.is_active and wp.rect.colliderect(block.rect):
                                    is_weak_point_hit_by_tower = True
                                    break # 弱点に当たっていたらループを抜ける

                        # --- 共通の衝突エフェクト ---
                        collision_point = (pygame.math.Vector2(enemy.rect.center) + pygame.math.Vector2(block.rect.center)) / 2
                        self._spawn_particles(collision_point, config.HIT_PARTICLE_COUNT, config.HIT_PARTICLE_LIFETIME, config.HIT_PARTICLE_MIN_SPEED, config.HIT_PARTICLE_MAX_SPEED, config.HIT_PARTICLE_GRAVITY, config.HIT_PARTICLE_START_SIZE, config.HIT_PARTICLE_END_SIZE, config.HIT_PARTICLE_COLORS_TOWER)
                        print(f"敵がタワーに衝突！")

                        # --- ダメージ処理 ---
                        # 敵が衝突したブロックにダメージを与える
                        block.take_damage(enemy.attack_power)

                        # タワーからの反撃ダメージ（弱点にヒットした場合は無効）
                        if not is_weak_point_hit_by_tower:
                            is_enemy_defeated = enemy.take_damage(config.TOWER_CONTACT_DAMAGE)
                            if is_enemy_defeated and not isinstance(enemy, BossEnemy):
                                self.enemies_defeated_count += 1
                        else:
                            print("タワーがボスの弱点に接触したが、ダメージは無効化された。")

                        # --- 共通のノックバックとアニメーション ---
                        # 敵をノックバックさせる
                        direction = pygame.math.Vector2(enemy.rect.center) - pygame.math.Vector2(block.rect.center)
                        if direction.length_squared() == 0: direction = pygame.math.Vector2(1, 0)
                        direction.normalize_ip()

                        # ボスかどうかでノックバックの力を変える
                        if isinstance(enemy, BossEnemy):
                            knockback_force = config.BOSS_TOWER_CONTACT_KNOCKBACK_FORCE
                        else:
                            knockback_force = config.TOWER_KNOCKBACK_FORCE
                        enemy.knockback(direction, knockback_force)

                        # ブロックのアニメーションを開始
                        block.start_animation()
                        break

    def _handle_bird_cloud_collision(self):
        for cloud in self.clouds:
            collided_puff_info = cloud.collide_with_bird(self.bird)
            if collided_puff_info:
                print("雲に衝突！")
                self.bird.bounce_off_cloud(collided_puff_info)
                self.bird.power_up()
                cloud.start_animation()
                break

    def _handle_bird_tower_collision(self):
        if self.bird.launch_time is not None:
            time_since_launch = pygame.time.get_ticks() - self.bird.launch_time
            if time_since_launch > config.TOWER_COLLISION_SAFE_TIME:
                for block in self.tower.blocks:
                    if self.bird.collide_and_bounce_off_rect(block, config.TOWER_BOUNCINESS):
                        self._spawn_particles(self.bird.pos, config.HIT_PARTICLE_COUNT, config.HIT_PARTICLE_LIFETIME, config.HIT_PARTICLE_MIN_SPEED, config.HIT_PARTICLE_MAX_SPEED, config.HIT_PARTICLE_GRAVITY, config.HIT_PARTICLE_START_SIZE, config.HIT_PARTICLE_END_SIZE, config.HIT_PARTICLE_COLORS_TOWER)
                        self.bird.power_up()
                        block.start_animation()
                        print("塔に衝突！")
                        break

    def _handle_bird_heart_collision(self):
        for i in range(len(self.heart_items) - 1, -1, -1):
            heart = self.heart_items[i]
            if heart.collide_with_bird(self.bird):
                print("ハートアイテムを獲得！")
                if self.tower.repair_one_block():
                    self._spawn_particles(heart.pos, config.PARTICLE_COUNT_ON_HEART_COLLECT, config.PARTICLE_LIFETIME, config.PARTICLE_MIN_SPEED, config.PARTICLE_MAX_SPEED, config.PARTICLE_GRAVITY, config.PARTICLE_START_SIZE, config.PARTICLE_END_SIZE, config.PARTICLE_COLORS)
                    del self.heart_items[i]
                    self.bird.power_up()
                    break

    def _handle_bird_enemy_collision(self):
        for enemy in reversed(self.enemies):
            # --- ボスとの衝突判定ロジック ---
            if isinstance(enemy, BossEnemy):
                # 1. アクティブな弱点との衝突判定を先に試みる
                hit_weak_point = False
                for wp in enemy.weak_points:
                    if wp.is_active and self.bird.collide_and_bounce_off_rect(wp, config.ENEMY_BOUNCINESS):
                        # --- コンボ処理 ---
                        new_combo_count = self.bird.increment_combo()
                        print(f"ボスの弱点に命中！ COMBO x{new_combo_count}")
                        # --- UI表示の呼び出し ---
                        if new_combo_count >= config.COMBO_MIN_TO_SHOW:
                            self.ui_manager.add_combo_indicator(self.bird.pos, new_combo_count)
                        self._spawn_particles(self.bird.pos, config.HIT_PARTICLE_COUNT, config.HIT_PARTICLE_LIFETIME, config.HIT_PARTICLE_MIN_SPEED, config.HIT_PARTICLE_MAX_SPEED, config.HIT_PARTICLE_GRAVITY, config.HIT_PARTICLE_START_SIZE, config.HIT_PARTICLE_END_SIZE, config.HIT_PARTICLE_COLORS_WEAK_POINT)

                        enemy.start_animation() # ボスをひるませる
                        is_enemy_defeated = enemy.take_damage(self.bird.attack_power)
                        self.bird.power_up() # 弱点に当てたらバードはダメージを受けずにパワーアップ
                        # ボスをノックバックさせる
                        direction = pygame.math.Vector2(enemy.rect.center) - self.bird.pos
                        if direction.length_squared() == 0: direction = pygame.math.Vector2(0, -1)
                        direction.normalize_ip()
                        force = config.BOSS_KNOCKBACK_FORCE + (self.bird.attack_power * config.ENEMY_KNOCKBACK_ATTACK_POWER_SCALE)
                        enemy.knockback(direction, force)
                        # 弱点の位置を即座に変更させる
                        enemy.force_switch_weak_point()

                        if is_enemy_defeated:
                            print("ボスを撃破した！")
                        hit_weak_point = True
                        break # 弱点ループを抜ける
                if hit_weak_point:
                    break # 敵ループも抜ける

                # 2. 弱点にヒットしなかった場合、ボス本体との衝突判定を行う
                if self.bird.collide_and_bounce_off_rect(enemy, config.BOSS_BODY_BOUNCINESS):
                    print("ボスの本体に命中！(ダメージなし)")
                    # ダメージ無しのヒットエフェクトを出す
                    self._spawn_particles(self.bird.pos, config.HIT_PARTICLE_COUNT, config.HIT_PARTICLE_LIFETIME, config.HIT_PARTICLE_MIN_SPEED, config.HIT_PARTICLE_MAX_SPEED, config.HIT_PARTICLE_GRAVITY, config.HIT_PARTICLE_START_SIZE, config.HIT_PARTICLE_END_SIZE, config.HIT_PARTICLE_COLORS_BOSS_BODY)
                    # ここではボスへのダメージ、ノックバック、バードのパワーアップは行わない
                    break # 敵ループを抜ける
            
            # --- 通常の敵との衝突判定 ---
            else:
                if self.bird.collide_and_bounce_off_rect(enemy, config.ENEMY_BOUNCINESS):
                    # --- コンボ処理 ---
                    new_combo_count = self.bird.increment_combo()
                    print(f"敵に衝突！ COMBO x{new_combo_count}")
                    # --- UI表示の呼び出し ---
                    if new_combo_count >= config.COMBO_MIN_TO_SHOW:
                        self.ui_manager.add_combo_indicator(self.bird.pos, new_combo_count)
                    self._spawn_particles(self.bird.pos, config.HIT_PARTICLE_COUNT, config.HIT_PARTICLE_LIFETIME, config.HIT_PARTICLE_MIN_SPEED, config.HIT_PARTICLE_MAX_SPEED, config.HIT_PARTICLE_GRAVITY, config.HIT_PARTICLE_START_SIZE, config.HIT_PARTICLE_END_SIZE, config.HIT_PARTICLE_COLORS_ENEMY)

                    enemy.start_animation()
                    is_enemy_defeated = enemy.take_damage(self.bird.attack_power)
                    is_bird_defeated = self.bird.take_damage(enemy.attack_power)
                    if not is_bird_defeated:
                        self.bird.power_up()
                    direction = pygame.math.Vector2(enemy.rect.center) - self.bird.pos
                    if direction.length_squared() == 0: direction = pygame.math.Vector2(0, -1)
                    direction.normalize_ip()
                    force = config.ENEMY_KNOCKBACK_FORCE + (self.bird.attack_power * config.ENEMY_KNOCKBACK_ATTACK_POWER_SCALE)
                    enemy.knockback(direction, force)
                    if is_enemy_defeated: self.enemies_defeated_count += 1
                    if is_bird_defeated: self.bird.reset(self.slingshot_pos)
                    break # 敵ループを抜ける

    def _handle_bird_ground_collision(self):
        # --- 発射直後の地面衝突を避けるためのセーフタイム処理 ---
        # 上方向に発射された場合のみ、一定時間は地面との衝突を無視する
        if self.bird.launched_upwards:
            if self.bird.launch_time is not None:
                time_since_launch = pygame.time.get_ticks() - self.bird.launch_time
                if time_since_launch < config.GROUND_COLLISION_SAFE_TIME:
                    return # セーフタイム中は衝突処理をスキップ

        # --- 通常の地面衝突処理 ---
        if self.bird.pos.y + self.bird.radius > config.GROUND_Y:
            if self.bird.velocity.y > config.GROUND_ANIMATION_MIN_VELOCITY_Y:
                self.ground.start_animation()

            self.bird.pos.y = config.GROUND_Y - self.bird.radius
            self.bird.velocity.y *= -config.BOUNCINESS
            self.bird.velocity.x *= config.FRICTION

    def _check_bird_reset(self):
        """弾がリセットされるべきか（画面外、停止）をチェックする。"""
        if not self.bird.is_flying:
            return

        is_off_screen = (self.bird.pos.x < -self.bird.radius or
                         self.bird.pos.x > config.SCREEN_WIDTH + self.bird.radius)
        if is_off_screen:
            self.bird.reset(self.slingshot_pos)
            return

        # --- 速度に基づくリセット判定 ---
        is_slow = self.bird.velocity.length_squared() < config.BIRD_RESET_MIN_VELOCITY_SQUARED
        is_on_ground = self.bird.pos.y + self.bird.radius >= config.GROUND_Y - 1

        if is_slow:
            # 1. 地面で低速になった場合は即時リセット
            if is_on_ground:
                self.bird.reset(self.slingshot_pos)
                return

            # 2. 空中で低速になった場合（スタック判定）
            # 低速タイマーがセットされていなければセット
            if self.bird.low_velocity_start_time is None:
                self.bird.low_velocity_start_time = pygame.time.get_ticks()
            
            # 低速状態が一定時間続いたらリセット
            if pygame.time.get_ticks() - self.bird.low_velocity_start_time > config.BIRD_STUCK_RESET_TIME:
                print("Bird seems to be stuck. Resetting.")
                self.bird.reset(self.slingshot_pos)
        else:
            # 速度が十分ある場合はタイマーをリセット
            self.bird.low_velocity_start_time = None

    def _cleanup_entities(self):
        """不要になったエンティティ（敵、パーティクル）をリストから削除する。"""
        # 寿命が尽きたパーティクルを削除
        self.particles[:] = [p for p in self.particles if p.is_alive()]

        # 死亡アニメーションが完了した、または画面外に出た敵を削除
        self.enemies[:] = [enemy for enemy in self.enemies if not enemy.is_finished() and enemy.rect.right > 0]

    def _transition_to_next_stage(self):
        """次のステージへの移行処理を行う。"""
        # 次のステージに進めるか試みる
        if not self.stage_manager.advance_stage():
            # 最終ステージをクリアした場合
            self.stage_state = "GAME_WON"
            print("Congratulations! You have beaten all stages!")
            return

        # --- 次のステージの準備 ---
        print(f"--- Preparing for Stage {self.stage_manager.current_stage} ---")
        
        # 次のステージの設定を取得
        settings = self.stage_manager.get_current_stage_settings()

        # 設定に基づいて雲を再配置するか決定
        if settings.get("rearrange_clouds", False):
            print("Rearranging clouds for the new stage.")
            self._generate_new_clouds()
        else:
            print("Keeping existing clouds for the new stage.")

        # タイマーとカウンターをリセット
        self.reset_level_state()
        
        # 前のステージのエンティティをクリア
        self.enemies.clear()
        self.heart_items.clear()
        self.particles.clear()

        # バードをリセット
        self.bird.reset(self.slingshot_pos)

    def _generate_new_clouds(self):
        """雲を新しく生成し、既存の雲リストを置き換える。"""
        slingshot_x = self.slingshot_pos.x
        tower_top_y = self.tower.get_top_y()

        # main.pyからインポートした共通関数で雲を生成
        new_clouds = create_cloud_layout(slingshot_x, tower_top_y)

        self.clouds.clear()
        self.clouds.extend(new_clouds)

    def _calculate_next_heart_spawn_time(self, current_time):
        """ステージ設定に基づき、次のハート出現時間を計算して返す。"""
        settings = self.stage_manager.get_current_stage_settings()
        # フォールバック用のデフォルト設定
        default_heart_settings = {"base": 10000, "random": 2000}
        heart_settings = settings.get("heart_spawn", default_heart_settings)

        base_interval = heart_settings.get("base", default_heart_settings["base"])
        random_range = heart_settings.get("random", default_heart_settings["random"])

        # random_rangeが0の場合はオフセットを0にする
        random_offset = random.uniform(-random_range, random_range) if random_range > 0 else 0
        
        interval = base_interval + random_offset
        # 負の間隔にならないように、0より大きいことを保証する
        return current_time + max(0, interval)

    def _spawn_particles(self, pos, count, lifetime, min_speed, max_speed, gravity, start_size, end_size, colors):
        """指定された設定でパーティクルを生成し、リストに追加する。"""
        for _ in range(count):
            self.particles.append(Particle(
                pos.x, pos.y,
                lifetime,
                min_speed,
                max_speed,
                gravity,
                start_size,
                end_size,
                colors
            ))

    @property
    def current_boss(self):
        """現在のボスインスタンスが存在すればそれを、なければNoneを返す。"""
        for enemy in self.enemies:
            if isinstance(enemy, BossEnemy):
                return enemy
        return None

    def jump_to_stage(self, stage_number):
        """指定されたステージにジャンプする（デバッグ用）。"""
        # ステージ番号が有効かチェック
        if stage_number in self.stage_manager.stages:
            self.stage_manager.current_stage = stage_number
            print(f"--- Jumping to Stage {self.stage_manager.current_stage} (Debug) ---")
            
            # 既存の移行処理を参考にリセット
            self.reset_level_state() # stage_stateをPLAYINGに戻す
            self.enemies.clear()
            self.heart_items.clear()
            self.particles.clear()
            self.bird.reset(self.slingshot_pos)
            
            # ステージクリア待機タイマーが存在すれば削除
            if hasattr(self, 'stage_clear_time'):
                del self.stage_clear_time
        else:
            print(f"Debug: Stage {stage_number} does not exist.")

    def _check_bird_callable(self):
        """弾が呼び戻し可能かチェックし、状態を更新する。"""
        if self.bird.is_flying:
            # 飛行中で、まだ呼び出し可能になっていない場合のみタイムアウトをチェック
            if not self.is_bird_callable:
                if pygame.time.get_ticks() - self.bird_last_active_time > config.BIRD_CALL_TIMEOUT:
                    self.is_bird_callable = True
                    print("Recall button is now available.")
        else:
            # 飛行中でなければ、タイマーをリセットし、呼び出し不可にする
            self.bird_last_active_time = pygame.time.get_ticks()
            if self.is_bird_callable:
                self.is_bird_callable = False
                print("Recall button is now hidden.")
