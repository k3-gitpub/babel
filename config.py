# --- 定数 ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
DEBUG = True # デバッグモードのフラグ。リリース時にはFalseに設定
DEBUG_START_STAGE = 1 # デバッグモード時に開始するステージ番号

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (211, 47, 47)
BLUE = (66, 165, 245)
GRAY = (158, 158, 158)
GREEN = (34, 139, 34)
GREEN_HOVER = (50, 180, 50) # ボタンホバー用の少し明るい緑
WOOD = (139, 69, 19)
YELLOW = (255, 235, 59)
AQUA = (0, 255, 255)
ORANGE = (255, 165, 0)
ORANGE_HOVER = (255, 200, 0) # ボタンホバー用の少し明るいオレンジ

# 物理定数
GRAVITY = 0.5
LAUNCH_POWER_MULTIPLIER = 0.3
FRICTION = 0.99 # 摩擦係数（1に近いほど滑る）
BOUNCINESS = 0.5 # 反発係数（0に近いほど跳ねない）

# オーディオ設定
BGM_VOLUME = 0.2 # BGMの音量 (0.0 ~ 1.0)
BGM_FADEOUT_MS = 500 # BGM切り替え時のフェードアウト時間 (ミリ秒)
BGM_NORMAL_PATH = "assets/audio/.ogg" # 通常BGMのパス
BGM_BOSS_PATH = "assets/audio/.ogg" # ボス戦BGMのパス
SE_VOLUME = 0.4 # SEの音量 (0.0 ~ 1.0)

# コンボヒット音の設定
USE_SCALE_SOUND_FOR_COMBO = False # True: ドレミ音階, False: 単一ヒット音
SE_COMBO_HIT_PATH = "assets/audio/jump3.ogg" # 単一ヒット音として使用するSEのパス
SE_COMBO_HIT_VOLUME = 0.2 # 単一ヒット音の音量 (0.0 ~ 1.0)

SCALE_SOUND_PATHS = [
    "assets/audio/scale_c.ogg",
    "assets/audio/scale_d.ogg",
    "assets/audio/scale_e.ogg",
    "assets/audio/scale_f.ogg",
    "assets/audio/scale_g.ogg",
    "assets/audio/scale_a.ogg",
    "assets/audio/scale_b.ogg",
    "assets/audio/scale_c2.ogg", # 高いド
    "assets/audio/scale_d2.ogg", # 高いレ
    "assets/audio/scale_e2.ogg", # 高いミ
]
SE_ENEMY_DEATH_PATH = "assets/audio/explosion.ogg" # 敵の死亡SE
SE_ENEMY_HIT_PATH = "assets/audio/dead.ogg" # 敵ヒットSE (死亡しなかった場合)
SE_TOWER_DAMAGE_PATH = "assets/audio/tower_damage.ogg" # タワーの被ダメージSE
SE_HEART_COLLECT_PATH = "assets/audio/heart_collect.ogg" # ハート取得SE
SE_STAGE_START_PATH = "assets/audio/.ogg" # ステージ開始SE
SE_SPEED_UP_COLLECT_PATH = "assets/audio/SpeedUP.ogg" # スピードアップ取得SE
SE_SIZE_UP_COLLECT_PATH = "assets/audio/GiantUP.ogg" # 巨大化取得SE
SE_ITEM_SPAWN_PATH = "assets/audio/item_spawn.ogg" # アイテム出現SE
SE_UI_CLICK_PATH = "assets/audio/select.ogg" # UIクリックSE

# タイトル画面設定
TITLE_ENEMY_SPAWN_INTERVAL = 8000 # にぎやかしの敵が出現する間隔 (ms)
TITLE_ENEMY_MAX_COUNT = 20         # にぎやかしの敵の最大数
TITLE_TOWER_BLOCKS = 7            # タイトル画面のタワーのブロック数

# 弾の設定
MAX_PULL_DISTANCE = 100 # スリングショットから引っ張れる最大距離
MIN_PULL_DISTANCE_TO_LAUNCH = 20 # 発射するために最低限必要なドラッグ距離
BIRD_DEFAULT_RADIUS = 20 # 弾の初期半径
SLINGSHOT_OFFSET_Y = -20 # 塔のてっぺんからのオフセット（負の値で上に）

# スリングショットの支柱設定
SLINGSHOT_POST_WIDTH = 10
SLINGSHOT_POST_HEIGHT = 20 # SLINGSHOT_OFFSET_Yの絶対値より大きいとタワーにめり込む
SLINGSHOT_POST_COLOR = WOOD

BIRD_POWER_UP_SCALE = 1.25 # 何かに当たるごとにボールが大きくなる倍率
BIRD_HP_MULTIPLIER = 10 # 弾の半径1あたりのHP
BIRD_ATTACK_POWER_MULTIPLIER = 7.5 # 弾の半径1あたりの攻撃力
BIRD_MAX_RADIUS = 60 # パワーアップ時のボールの最大半径
BIRD_POWER_UP_COOLDOWN = 500 # パワーアップのクールダウン時間 (ミリ秒)
BIRD_RESET_MIN_VELOCITY_SQUARED = 2 # 弾がこの速度(の2乗)以下になったらリセットされる
BIRD_STUCK_RESET_TIME = 500 # 弾が空中で停止したとみなしてリセットするまでの時間 (ミリ秒)
BIRD_CALL_TIMEOUT = 2000 # 弾を呼び戻せるようになるまでの時間 (ミリ秒)

# 画面端でのバウンド設定 (実験用)
ENABLE_SIDE_WALL_BOUNCE = True # Trueにすると画面の左右の壁でボールがバウンドする
SIDE_WALL_BOUNCINESS = 0.8 # 画面端での反発係数
SIDE_WALL_DAMAGE = 100 # 画面端の壁に衝突した際に受けるダメージ

GROUND_COLLISION_SAFE_TIME = 500 # 発射後に地面との衝突判定が有効になるまでの時間 (ミリ秒)
TOWER_COLLISION_SAFE_TIME = 500 # 発射後に塔との衝突判定が有効になるまでの時間 (ミリ秒)

# 弾の目の設定
BIRD_EYE_OUTLINE_WIDTH = 2
BIRD_EYE_SIZE_SCALE = 0.4  # 弾の半径に対する目の半径の比率
BIRD_EYE_OFFSET_X_SCALE = 0.4 # 弾の中心からのXオフセット比率 (半径に対する)
BIRD_EYE_OFFSET_Y_SCALE = 0.0 # 弾の中心からのYオフセット比率 (半径に対する)
BIRD_PUPIL_SIZE_SCALE = 0.5 # 白目に対する黒目の半径の比率
BIRD_PUPIL_MAX_OFFSET_SCALE = 0.3 # 黒目が動く度合い (0=中央固定, 1=白目の縁に接する)

# 弾の回転設定
BIRD_ANGULAR_FRICTION = 0.98 # 空中での回転の減衰係数 (1に近いほど止まりにくい)
BIRD_COLLISION_SPIN_FACTOR = 0.1 # 衝突時に接線速度から回転に変換する係数

# 軌道ガイドの設定
TRAJECTORY_NUM_POINTS = 10  # 軌道を示す点の数
TRAJECTORY_POINT_GAP = 5    # 軌道計算のステップ間隔（大きいほど点の間隔が広がる）
TRAJECTORY_POINT_RADIUS = 5 # 軌道を示す点の半径

# 呼び戻しボタンの設定
RECALL_BUTTON_SIZE = (120, 40)
RECALL_BUTTON_COLOR = (244, 143, 177) # ピンク系
RECALL_BUTTON_TEXT_COLOR = WHITE
RECALL_BUTTON_OFFSET_Y = 40 # スリングショットからのY方向のオフセット（正の値で上に）

# 塔の設定
SLINGSHOT_X = 180 # スリングショットのX座標。タワーの位置の基準にもなる。
TOWER_BLOCK_WIDTH = 40
TOWER_BLOCK_HEIGHT = 40
TOWER_INITIAL_BLOCKS = 3 # タワーの初期ブロック数
TOWER_CONTACT_DAMAGE = 40 # タワーが接触時に敵に与えるダメージ
TOWER_KNOCKBACK_FORCE = 20 # タワーが敵に衝突した際に与えるノックバック（押し返す力）の基本強度
BOSS_TOWER_CONTACT_KNOCKBACK_FORCE = 30 # ボスがタワーに衝突した際のノックバック力
TOWER_BOUNCINESS = 1.2 # 塔の反発係数

# 塔のブロック個別の設定
BLOCK_HP = 200
BLOCK_DEATH_EFFECT_DURATION = 200 # 死亡エフェクトの時間 (ミリ秒)
BLOCK_DEATH_EFFECT_COLOR = (255, 100, 100) # エフェクトの色 (灰色)
BLOCK_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER = 2.0 # ブロックサイズに対する最大半径の倍率
BLOCK_DEATH_EFFECT_LINE_WIDTH = 4 # 死亡エフェクトの円の線の太さ

# 塔のブロックの窓の設定
BLOCK_WINDOW_COLOR = (180, 180, 250) # 窓の色 ()
BLOCK_WINDOW_WIDTH_RATIO = 0.35 # ブロックの幅に対する窓の幅の比率
BLOCK_WINDOW_HEIGHT_RATIO = 0.5 # ブロックの高さに対する窓の高さの比率
BLOCK_WINDOW_OUTLINE_WIDTH = 2 # 窓の枠線の太さ

# 塔のアニメーション設定
TOWER_ANIMATION_DURATION = 300 # 塔が元の大きさに戻るまでの時間 (ミリ秒)
TOWER_ANIMATION_MIN_SCALE = 0.75 # 衝突時に縮む最小スケール

# 塔のライフ（ハート）表示設定
TOWER_HEART_START_X = 140 # 最初のハートのX座標
TOWER_HEART_Y = 680       # 全てのハートのY座標
TOWER_HEART_SIZE = 30     # ハートの大きさ
TOWER_HEART_SPACING = 40  # ハート同士の間隔
TOWER_HEART_COLOR = (255, 105, 180) # ハートの色 (ホットピンク)

# 地面のアニメーション設定
GROUND_Y = 650 # 地面のY座標
GROUND_ANIMATION_DURATION = 80 # 地面が元の大きさに戻るまでの時間 (ミリ秒)
GROUND_ANIMATION_MIN_SCALE = 0.95 # 衝突時に縮む最小スケール
GROUND_ANIMATION_MIN_VELOCITY_Y = 5.0 # 地面のアニメーションが開始される最低垂直速度

# 雲の設定
CLOUD_COLLISION_SAFE_TIME = 150 # 発射後に雲との衝突判定が有効になるまでの時間 (ミリ秒)
CLOUD_BOUNCINESS = 1.05 # 雲の反発係数

# 雲のアニメーション設定
CLOUD_ANIMATION_DURATION = 600 # 雲が元の大きさに戻るまでの時間 (ミリ秒)
CLOUD_ANIMATION_MIN_SCALE = 0.8 # 衝突時に縮む最小スケール

# 雲の生成設定
CLOUD_MIN_COUNT = 5 # 生成される雲の最小数
CLOUD_MAX_COUNT = 7 # 生成される雲の最大数
CLOUD_MIN_DISTANCE_X = 250 # 生成される雲同士の最低距離 (X軸方向)
CLOUD_MIN_DISTANCE_Y = 200 # 生成される雲同士の最低距離 (Y軸方向)
CLOUD_SPAWN_PADDING_X = 100 # 画面の左右の端から雲が生成されるまでの最低距離
CLOUD_SPAWN_Y_MIN = 150  # 雲が生成されるY座標の上限（画面上部）
CLOUD_SPAWN_Y_MAX = 450 # 雲が生成されるY座標の下限（画面下部）
CLOUD_MIN_DISTANCE_FROM_TOWER = 300 # 塔から雲が生成されるまでの最低距離（円範囲）

# 雲の浮遊アニメーション設定
CLOUD_FLOAT_SPEED = 0.01 # ふわふわ動く速さ
CLOUD_FLOAT_AMPLITUDE = 4 # ふわふわ動く振れ幅（ピクセル単位）

# UI設定
UI_COUNTER_OUTLINE_WIDTH = 2 # 討伐数カウンターのアウトラインの太さ
UI_TITLE_OUTLINE_WIDTH = 3 # タイトルテキストのアウトラインの太さ

# DRAG表示設定
DRAG_TEXT_FONT_SIZE = 48 # "DRAG"の文字サイズ
DRAG_TEXT_BLINK_INTERVAL = 600 # 点滅の間隔 (ms)
DRAG_TEXT_COLOR = WHITE
DRAG_PROMPT_DELAY = 2000 # 入力がない場合にDRAG表示を再表示するまでの待機時間 (ms)

# コンボ表示設定
COMBO_DURATION = 1000 # コンボ表示の持続時間 (ms)
COMBO_MOVE_Y = 160 # コンボ表示が上に移動する距離 (pixels)
COMBO_START_COLOR = (255, 255, 0) # テキストの初期色 (黄色)
COMBO_END_COLOR = (255, 165, 0) # テキストの終末色 (オレンジ)
COMBO_OUTLINE_COLOR = (0, 0, 0)
COMBO_OUTLINE_WIDTH = 2
COMBO_TEXT_FONT_SIZE = 36 # "x" と "COMBO!" の文字サイズ
COMBO_NUMBER_BASE_FONT_SIZE = 48 # コンボ数の基本サイズ
COMBO_MIN_TO_SHOW = 2 # 表示を開始する最低コンボ数
COMBO_NUMBER_SCALE_FACTOR = 1.5 # コンボ数1あたりのフォントサイズ増加率
COMBO_NUMBER_MAX_ADDITIONAL_SIZE = 100 # フォントサイズの最大増加量

# スコアポップアップ表示設定
SCORE_INDICATOR_DURATION = 800 # 表示の持続時間 (ms)
SCORE_INDICATOR_MOVE_Y = 80 # 上に移動する距離 (pixels)
SCORE_INDICATOR_COLOR = (255, 100, 100) # テキストの色 (薄い黄色)
SCORE_INDICATOR_FONT_SIZE = 64
SCORE_INDICATOR_OUTLINE_COLOR = BLACK
SCORE_INDICATOR_OUTLINE_WIDTH = 2

# スコア計算設定
SCORE_BASE_POINTS = {
    "enemy": 100,             # 通常の敵を倒した時の基本点
    "boss_weak_point": 250,   # ボスの弱点にヒットした時の基本点
}
SCORE_COMBO_LINEAR_BONUS = 20 # コンボ数ごとの線形ボーナス (例: 2コンボなら+20, 3コンボなら+40)
SCORE_COMBO_TIER_BONUS = {    # コンボ数に応じた段階的ボーナス
    5: 50,   # 5コンボ以上で+100
    10: 100,  # 10コンボ以上で+300
    20: 300, # 20コンボ以上で+1000
}
SCORE_TOWER_BONUS_PER_BLOCK = 100 # ゲームクリア時のタワーのブロック1つあたりのボーナス点


# ボス戦UI設定
BOSS_UI_TITLE_COLOR = (255, 87, 34) # ボスタイトルの色 (Deep Orange)
BOSS_NAME_FONT_SIZE = 32 # ボスの名前のフォントサイズ
BOSS_NAME_OFFSET_Y = 0 # HPバーからのYオフセット（負の値で上に）
BOSS_HP_BAR_WIDTH = 400
BOSS_HP_BAR_HEIGHT = 20
BOSS_HP_BAR_Y = 30
BOSS_HP_BAR_BG_COLOR = (50, 50, 50)
BOSS_HP_BAR_COLOR = (211, 47, 150) # 
BOSS_HP_BAR_OUTLINE_WIDTH = 3

# 3つ目のボスの弱点の描画設定
WEAK_POINT_SIZE = 60
WEAK_POINT_EYE_WHITE_COLOR = (255, 255, 255) # 白
WEAK_POINT_PUPIL_COLOR = (0, 0, 0) # 黒
WEAK_POINT_PUPIL_RADIUS_SCALE = 0.4 # 白目に対する黒目の半径の比率
WEAK_POINT_COLOR_INACTIVE = (80, 80, 80) # ダークグレー
WEAK_POINT_OUTLINE_WIDTH = 3
WEAK_POINT_CLOSED_LINE_WIDTH = 4 # 閉じた瞼の線の太さ
BOSS_WEAK_POINT_OFFSET = 5 # ボスの縁から弱点が内側にめり込む距離

# 3つ目のボスの弱点設定
WEAK_POINT_SWITCH_INTERVAL = 8000 # 弱点が切り替わる間隔 (ms)。短いほど難易度が上がる。
BOSS_KNOCKBACK_FORCE = 20.0 # ボスが弱点に攻撃を受けた際のノックバックの基本強度。大きいほど後ろに下がる。
BOSS_SCALE_REDUCTION_ON_HIT = 0.1 # 弱点に1回ヒットした際の縮小率。大きいほど早く小さくなる。
BOSS_MIN_SCALE = 0.2 # ボスの最小スケール。これ以上は小さくならない。
BOSS_BODY_BOUNCINESS = 1.1 # ボス本体に当たった時の弾の反発係数

# 3つ目のボス敵自体の設定
BOSS_SIZE = 300
BOSS_MAX_HP = 500
BOSS_BASE_SPEED = 0.1
BOSS_SPEED_SCALE_MULTIPLIER = 5.0 # スケール減少に応じた速度上昇の倍率。1.0なら線形に増加、2.0ならより急激に増加。
BOSS_ATTACK_POWER = 300 # ボスの攻撃力
BOSS_BODY_CONTACT_DAMAGE_TO_BIRD = 100 # ボス本体にボールが接触した際にボールが受けるダメージ

# ボスの天使の輪の設定
BOSS_HALO_OFFSET_Y = -80 # ボスのてっぺんからのYオフセット
BOSS_HALO_WIDTH_SCALE = 0.5 # ボスの幅に対する輪の幅の比率
BOSS_HALO_HEIGHT_SCALE = 0.15 # ボスの幅に対する輪の高さの比率
BOSS_HALO_FLOAT_SPEED = 0.05 # ふわふわ動く速さ
BOSS_HALO_FLOAT_AMPLITUDE = 5 # ふわふわ動く振れ幅
BOSS_HALO_LINE_WIDTH = 10 # 輪の線の太さ
BOSS_HALO_COLOR = (255, 235, 59) # 黄色 (YELLOWと同じ)

# ステージ設定
STAGE_CLEAR_WAIT_TIME = 2500 # ステージクリア表示から次のステージへ移るまでの時間 (ms)


# 敵の設定
ENEMY_SPAWN_INTERVAL = 5000 # 敵が出現する間隔 (ミリ秒)
FIRST_ENEMY_SPAWN_DELAY = 500 # 最初の敵が出現するまでの時間 (ミリ秒)
ENEMY_SPAWN_OFFSET_X = 20 # 画面右端からどれだけ離れて出現するか
ENEMY_MIN_SIZE = 40 # 敵の最小サイズ
ENEMY_MAX_SIZE = 120 # 敵の最大サイズ
ENEMY_HP_MULTIPLIER = 2 # サイズに対するHPの倍率
ENEMY_SPEED_BASE = 40 # 敵の基本速度（この値をサイズで割る）
ENEMY_MIN_SPEED = 0.1 # 敵の最低移動速度
ENEMY_ATTACK_MULTIPLIER = 1.5 # サイズに対する攻撃力の倍率
ENEMY_BOUNCINESS = 0.75 # 敵に当たった時の弾の反発係数
ENEMY_KNOCKBACK_FORCE = 1.0 # 敵が受けるノックバックの基本強度
ENEMY_KNOCKBACK_ATTACK_POWER_SCALE = 0.1 # ノックバックの力に対する弾の攻撃力の影響係数
ENEMY_FRICTION = 0.9 # ノックバックされた敵の減速係数
ENEMY_GROUND_BOUNCINESS = 0.4 # 敵が地面でバウンドする際の反発係数
ENEMY_GROUND_FRICTION = 0.75 # 敵が地面を滑るときの摩擦係数

# 敵の目の設定 (共通)
ENEMY_EYE_WHITE_COLOR = (255, 255, 255)
ENEMY_EYE_PUPIL_COLOR = (0, 0, 0)
ENEMY_EYE_PUPIL_SCALE = 0.5 # 白目に対する黒目の大きさの比率
ENEMY_EYE_OUTLINE_WIDTH = 2
GROUND_ENEMY_EYE_SIZE_SCALE = 0.25 # 敵の幅に対する目の半径の比率
GROUND_ENEMY_EYE_OFFSET_X_SCALE = -0.18 # 敵の中心からのXオフセット比率
GROUND_ENEMY_EYE_OFFSET_Y_SCALE = -0.05 # 敵の中心からのYオフセット比率

# 飛行する敵の設定
FLYING_ENEMY_MIN_Y = 50 # 飛行する敵が出現するY座標の最小値
FLYING_ENEMY_MAX_Y = 450 # 飛行する敵が出現するY座標の最大値
# FLYING_ENEMY_ATTACK_RANGE = 450 # 飛行する敵がタワーへの攻撃を開始する距離
# 攻撃を開始するタワーからのX軸距離の範囲
FLYING_ENEMY_ATTACK_RANGE_MAX = 450 # 最も遠い攻撃開始距離
FLYING_ENEMY_ATTACK_RANGE_MIN = -150 # 最も近い攻撃開始距離（負の値でタワーを通り過ぎてから攻撃）
# 攻撃時のターゲットY座標オフセットの範囲（タワーのてっぺんを基準とする）
FLYING_ENEMY_TARGET_Y_MIN = -80 # 最小オフセット（負の値でタワーの上方を狙う）
FLYING_ENEMY_TARGET_Y_MAX = 120 # 最大オフセット（正の値でタワーの下方を狙う）
FLYING_ENEMY_ROTATION_SPEED = 3.0 # 敵が向きを変える速さ（度/フレーム）
FLYING_ENEMY_MIN_SIZE = 40
FLYING_ENEMY_MAX_SIZE = 100
FLYING_ENEMY_HP_MULTIPLIER = 1.5
FLYING_ENEMY_SPEED_BASE = 30
FLYING_ENEMY_MIN_SPEED = 0.1
FLYING_ENEMY_ATTACK_MULTIPLIER = 1.5
FLYING_ENEMY_COLOR = (156, 39, 176) # 紫色
FLYING_ENEMY_OUTLINE_WIDTH = 2 # 飛行する敵の枠線の太さ
FLYING_ENEMY_EYE_SIZE_SCALE = 0.2 # 敵のサイズに対する目の半径の比率

# ジャンパー（ジャンプする敵）の設定
JUMPING_ENEMY_COLOR = GREEN # 緑色
JUMPING_ENEMY_MIN_SIZE = 40
JUMPING_ENEMY_MAX_SIZE = 120
JUMPING_ENEMY_MIN_JUMP_FORCE = -10 # ジャンプ力の最小値（負の値で上方向）
JUMPING_ENEMY_MAX_JUMP_FORCE = -20 # ジャンプ力の最大値
JUMPING_ENEMY_JUMP_COOLDOWN_MIN = 1000 # 次のジャンプまでの待機時間の最小値 (ms)
JUMPING_ENEMY_JUMP_COOLDOWN_MAX = 3000 # 次のジャンプまでの待機時間の最大値 (ms)

# ジャンパー専用のステータス倍率
JUMPING_ENEMY_HP_MULTIPLIER = 3
JUMPING_ENEMY_ATTACK_MULTIPLIER = 1.5
JUMPING_ENEMY_SPEED_BASE = 80 # ジャンプ時の横方向の移動速度の基準値

# ジャンパーの目の設定 (共通)
JUMPING_ENEMY_EYE_SIZE_SCALE = 0.5 # 敵の幅に対する目の半径の比率
JUMPING_ENEMY_EYE_OFFSET_X_SCALE = 0 # 敵の中心からのXオフセット比率
JUMPING_ENEMY_EYE_OFFSET_Y_SCALE = 0 # 敵の中心からのYオフセット比率

# 敵のアニメーション設定
ENEMY_ANIMATION_DURATION = 300 # 敵が元の大きさに戻るまでの時間 (ミリ秒)
ENEMY_ANIMATION_MIN_SCALE = 0.7 # 衝突時に縮む最小スケール

# 敵の死亡エフェクト設定
ENEMY_DEATH_EFFECT_DURATION = 200 # 死亡エフェクトの時間 (ミリ秒)
ENEMY_DEATH_EFFECT_MAX_RADIUS_MULTIPLIER = 1.5 # 敵のサイズに対する最大半径の倍率
ENEMY_DEATH_EFFECT_COLOR = (255, 100, 100) # エフェクトの色
ENEMY_DEATH_EFFECT_LINE_WIDTH = 5 # 死亡エフェクトの円の線の太さ (0にすると塗りつぶし)

# ハートアイテムの設定
ITEM_Y_OFFSET = -15 # 雲のてっぺんからのオフセット（負の値で上に）
HEART_ITEM_SIZE = 40 # ハートアイテムの大きさ
HEART_ITEM_COLOR = (255, 105, 180) # ハートアイテムの色 (ホットピンク)
HEART_ITEM_OUTLINE_WIDTH = 2 # ハートアイテムの輪郭線の太さ

# スピードアップアイテムの設定
SPEED_UP_ITEM_SIZE = 40
SPEED_UP_ITEM_COLOR = (255, 235, 59) # 黄色
SPEED_UP_ITEM_OUTLINE_COLOR = BLACK
SPEED_UP_ITEM_OUTLINE_WIDTH = 2

# 巨大化アイテムの設定
SIZE_UP_ITEM_SIZE = 40
SIZE_UP_ITEM_COLOR = (100, 221, 23) # 明るい緑
SIZE_UP_ITEM_OUTLINE_COLOR = BLACK
SIZE_UP_ITEM_OUTLINE_WIDTH = 2

# アイテム効果設定
SPEED_BOOST_MULTIPLIER = 2.0 # 速度の増加倍率
SIZE_BOOST_DURATION = 5000 # 巨大化の持続時間 (ms)

# ハート取得パーティクルエフェクトの設定
PARTICLE_COUNT_ON_HEART_COLLECT = 25 # ハート取得時に出現するパーティクルの数
PARTICLE_LIFETIME = 40 # パーティクルの寿命（フレーム数）
PARTICLE_MIN_SPEED = 1.0 # パーティクルの最低速度
PARTICLE_MAX_SPEED = 4.0 # パーティクルの最大速度
PARTICLE_GRAVITY = 0.1 # パーティクルにかかる重力
PARTICLE_START_SIZE = 7 # パーティクルの初期サイズ
PARTICLE_END_SIZE = 0 # パーティクルの終末サイズ
PARTICLE_COLORS = [(255, 255, 0), (255, 215, 0), (255, 255, 255), (255, 182, 193)] # 黄色、金色、白、ライトピンク

# ヒットエフェクト用パーティクルの設定
HIT_PARTICLE_COUNT = 10
HIT_PARTICLE_LIFETIME = 20
HIT_PARTICLE_MIN_SPEED = 1.5
HIT_PARTICLE_MAX_SPEED = 5.0
HIT_PARTICLE_GRAVITY = 0
HIT_PARTICLE_START_SIZE = 5
HIT_PARTICLE_END_SIZE = 0
HIT_PARTICLE_COLORS_ENEMY = [(255, 82, 82), (183, 28, 28)] # 赤系
HIT_PARTICLE_COLORS_TOWER = [(200, 200, 200), (150, 150, 150)] # 白/灰色系
HIT_PARTICLE_COLORS_BOSS_BODY = [(120, 120, 120), (150, 150, 150)] # ボス本体用の灰色系
HIT_PARTICLE_COLORS_WEAK_POINT = [(0, 255, 255), (179, 229, 252)] # シアン/ライトブルー系
HIT_PARTICLE_COLORS_WALL = [(100, 100, 255), (150, 150, 255)] # 壁用の青系

# コンボゲージ設定
COMBO_GAUGE_MAX = 1000
COMBO_GAUGE_INCREASE_BASE = 25
COMBO_GAUGE_INCREASE_PER_COMBO = 15

# コンボゲージUI設定
COMBO_GAUGE_WIDTH = 200
COMBO_GAUGE_HEIGHT = 20
COMBO_GAUGE_X = SCREEN_WIDTH / 2
COMBO_GAUGE_Y = SCREEN_HEIGHT - 40
COMBO_GAUGE_BG_COLOR = (50, 50, 50)
COMBO_GAUGE_COLOR = BLUE
COMBO_GAUGE_OUTLINE_COLOR = BLACK
COMBO_GAUGE_OUTLINE_WIDTH = 2
COMBO_GAUGE_FLASH_COLOR = WHITE
COMBO_GAUGE_FLASH_DURATION = 750 # ms
COMBO_GAUGE_TEXT_BASE_FONT_SIZE = 24
COMBO_GAUGE_TEXT_PULSE_ADDITIONAL_SIZE = 48 # 満タン時に基本サイズにこの値が加算される
ITEM_SPAWN_DELAY_AFTER_GAUGE_MAX = 500 # ゲージ満タン演出が終わってからアイテムが出現するまでの待機時間(ms)

# SEパス
SE_GAUGE_MAX_PATH = "assets/audio/gauge_max.ogg"

# アイテム出現アニメーション設定
ITEM_SPAWN_ANIMATION_DURATION = 750 # ms
ITEM_SPAWN_ANIMATION_MAX_SCALE = 2.5 # 出現時に最大でこの倍率まで大きくなる

# アイテム出現設定
ITEM_SPAWN_CHANCES = {
    "heart": 0.5,      
    "speed_up": 0.3,   
    "size_up": 0.2     
}

# 空中アイテム出現ゾーン設定
AIR_ITEM_SPAWN_X_MIN = 300
AIR_ITEM_SPAWN_X_MAX = SCREEN_WIDTH - 100
AIR_ITEM_SPAWN_Y_MIN = 200
AIR_ITEM_SPAWN_Y_MAX = 500
