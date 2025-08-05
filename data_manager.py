import json
import os
from typing import Dict, Any

class DataManager:
    """
    ゲームのセーブデータ（ハイスコア、ベストコンボ）をファイルに読み書きするクラス。
    """
    DEFAULT_DATA: Dict[str, Any] = {
        "high_score": 0,
        "best_combo": 0,
        "best_tower_height": 0,
        "sound_enabled": True
    }

    def __init__(self, filename: str = "save_data.json"):
        """
        DataManagerを初期化する。
        :param filename: セーブデータのファイル名
        """
        self.filename = filename
        
    def load_data(self) -> Dict[str, Any]:
        """
        セーブデータをファイルから読み込む。
        ファイルが存在しない、または中身が不正な場合は初期データを返す。
        :return: セーブデータの辞書
        """
        if not os.path.exists(self.filename):
            print(f"セーブファイル '{self.filename}' が見つかりません。初期データを作成します。")
            return self.DEFAULT_DATA.copy()

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # 読み込んだデータにデフォルト値をマージして、キーの欠損に対応する
                loaded_data = self.DEFAULT_DATA.copy()
                loaded_data.update(data)
                print(f"セーブファイル '{self.filename}' を正常に読み込みました。")
                return loaded_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"セーブファイル '{self.filename}' の読み込みに失敗しました: {e}。初期データを作成します。")
            return self.DEFAULT_DATA.copy()

    def save_data(self, data: Dict[str, Any]) -> None:
        """
        指定されたデータをファイルに保存する。
        :param data: 保存するデータの辞書
        """
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"データを '{self.filename}' に正常に保存しました。")
        except IOError as e:
            print(f"データ '{self.filename}' の保存に失敗しました: {e}")