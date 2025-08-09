import json
import os
from typing import Dict, Any

class DataManager:
    """Manages reading and writing game save data (e.g., high score, best combo)."""
    DEFAULT_DATA: Dict[str, Any] = {
        "high_score": 0,
        "best_combo": 0,
        "best_tower_height": 0,
        "sound_enabled": True
    }

    def __init__(self, filename: str = "save_data.json"):
        """Initializes the DataManager.

        :param filename: The name of the save data file.
        """
        self.filename = filename
        
    def load_data(self) -> Dict[str, Any]:
        """Loads save data from a file.
        Returns default data if the file doesn't exist or is corrupt.
        :return: A dictionary containing the save data.
        """
        if not os.path.exists(self.filename):
            print(f"Save file '{self.filename}' not found. Creating initial data.")
            return self.DEFAULT_DATA.copy()

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # 読み込んだデータにデフォルト値をマージして、キーの欠損に対応する
                loaded_data = self.DEFAULT_DATA.copy()
                loaded_data.update(data)
                print(f"Successfully loaded save file '{self.filename}'.")
                return loaded_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load save file '{self.filename}': {e}. Creating initial data.")
            return self.DEFAULT_DATA.copy()

    def save_data(self, data: Dict[str, Any]) -> None:
        """Saves the given data to the file.

        :param data: The dictionary of data to save.
        """
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data successfully saved to '{self.filename}'.")
        except IOError as e:
            print(f"Failed to save data to '{self.filename}': {e}")