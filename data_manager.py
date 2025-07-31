import json
import os

class DataManager:
    """
    ゲームのセーブデータ（ハイスコア、ベストコンボ）をファイルに読み書きするクラス。
    """
    def __init__(self, filename="save_data.json"):
        """
        DataManagerを初期化する。
        :param filename: セーブデータのファイル名
        """
        self.filename = filename

    def load_data(self):
        """
        セーブデータをファイルから読み込む。
        ファイルが存在しない、または中身が不正な場合は初期データを返す。
        :return: セーブデータの辞書
        """
        if not os.path.exists(self.filename):
            print(f"セーブファイル '{self.filename}' が見つかりません。初期データを作成します。")
            return {"high_score": 0, "best_combo": 0}

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # 念のため、キーが存在するかチェック
                if "high_score" not in data or "best_combo" not in data:
                    print(f"セーブファイル '{self.filename}' の形式が不正です。初期データで上書きします。")
                    return {"high_score": 0, "best_combo": 0}
                print(f"セーブファイル '{self.filename}' を正常に読み込みました。")
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"セーブファイル '{self.filename}' の読み込みに失敗しました: {e}。初期データを作成します。")
            return {"high_score": 0, "best_combo": 0}

    def save_data(self, data):
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