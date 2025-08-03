import json
import os
import platform
import asyncio

class DataManager:
    """
    ゲームのセーブデータを読み書きするクラス。
    PC環境ではJSONファイルを、Webブラウザ環境ではブラウザのストレージ(IndexedDB)を使用する。
    """
    def __init__(self, filename="save_data.json"):
        self.filename = filename
        self.is_web = platform.system() == "Emscripten"
        if self.is_web:
            print("DataManager: Web環境を検出。ブラウザのストレージを使用します。")
        else:
            print("DataManager: PC環境を検出。ローカルファイルを使用します。")

    async def load_data(self):
        """
        セーブデータを読み込む。WebとPCで処理を分岐する。
        ファイル/データが存在しない、または中身が不正な場合は初期データを返す。
        :return: セーブデータの辞書
        """
        if self.is_web:
            # --- Webブラウザからの読み込み ---
            try:
                # pygbagのストレージ機能は非同期なのでawaitが必要
                await asyncio.sleep(0) # ストレージAPIの準備を待つための小さな待機
                high_score = await asyncio.storage.get("high_score")
                best_combo = await asyncio.storage.get("best_combo")
                sound_enabled = await asyncio.storage.get("sound_enabled")
                best_tower_height = await asyncio.storage.get("best_tower_height")

                # データが存在しない場合はNoneが返るので、デフォルト値を設定
                data = {
                    "high_score": int(high_score) if high_score is not None else 0,
                    "best_combo": int(best_combo) if best_combo is not None else 0,
                    "sound_enabled": bool(int(sound_enabled)) if sound_enabled is not None else True,
                    "best_tower_height": int(best_tower_height) if best_tower_height is not None else 0
                }
                print(f"ブラウザストレージからデータを読み込みました: {data}")
                return data
            except Exception as e:
                print(f"ブラウザストレージからの読み込みに失敗しました: {e}。初期データを使用します。")
                return {"high_score": 0, "best_combo": 0, "sound_enabled": True, "best_tower_height": 0}
        else:
            # --- ローカルファイルからの読み込み (同期処理) ---
            if not os.path.exists(self.filename):
                print(f"セーブファイル '{self.filename}' が見つかりません。初期データを作成します。")
                return {"high_score": 0, "best_combo": 0, "sound_enabled": True, "best_tower_height": 0}

            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # 念のため、キーが存在するかチェック
                    if "high_score" not in data or "best_combo" not in data or "sound_enabled" not in data:
                        print(f"セーブファイル '{self.filename}' の形式が不正です。初期データで上書きします。")
                        return {"high_score": 0, "best_combo": 0, "sound_enabled": True, "best_tower_height": 0}
                    print(f"セーブファイル '{self.filename}' を正常に読み込みました。")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"セーブファイル '{self.filename}' の読み込みに失敗しました: {e}。初期データを作成します。")
                return {"high_score": 0, "best_combo": 0, "sound_enabled": True, "best_tower_height": 0}

    async def save_data(self, data):
        """
        指定されたデータを保存する。WebとPCで処理を分岐する。
        :param data: 保存するデータの辞書
        """
        if self.is_web:
            # --- Webブラウザへの保存 ---
            try:
                # pygbagのストレージ機能は非同期なのでawaitが必要
                for key, value in data.items():
                    # bool値は1/0の文字列として保存するのが安全
                    if isinstance(value, bool):
                        await asyncio.storage.set(key, "1" if value else "0")
                    else:
                        await asyncio.storage.set(key, str(value))
                # 変更を永続化
                await asyncio.storage.sync()
                print(f"データをブラウザストレージに保存しました: {data}")
            except Exception as e:
                print(f"ブラウザストレージへの保存に失敗しました: {e}")
        else:
            # --- ローカルファイルへの保存 (同期処理) ---
            try:
                with open(self.filename, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"データを '{self.filename}' に正常に保存しました。")
            except IOError as e:
                print(f"データ '{self.filename}' の保存に失敗しました: {e}")