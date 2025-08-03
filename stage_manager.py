# stage_manager.py
import difficulty_config
import config

class StageManager:
    """
    ゲームのステージ進行と難易度を管理するクラス。
    """
    def __init__(self):
        """StageManagerを初期化する。"""
        self.stages = difficulty_config.STAGES
        self.current_stage = 1
        print("StageManager initialized.")

    def get_current_stage_settings(self):
        """現在のステージの設定データを返す。"""
        return self.stages.get(self.current_stage)

    def advance_stage(self):
        """次のステージに進む。"""
        next_stage_number = self.current_stage + 1
        if next_stage_number in self.stages:
            self.current_stage = next_stage_number
            print(f"Stage advanced to {self.current_stage}")
            return True
        else:
            print(f"Stage {self.current_stage} was the final stage.")
            return False # 次のステージが存在しない場合

    def reset_stages(self):
        """ステージを1に戻す。"""
        self.current_stage = 1
        print("Stages reset to 1.")