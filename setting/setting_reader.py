import json
from pathlib import Path
from typing import Any

from PySide6.QtGui import QFont


class Setting:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.user_setting_path = self.root_path / "user_data/user_setting.json"
        self.default_path = self.root_path / "setting/default.json"
        self.initialize()
        with open(self.default_path, "r", encoding="utf-8") as f:
            self.default = json.load(f)
        with open(self.user_setting_path, "r", encoding="utf-8") as f:
            self.user = json.load(f)

    def initialize(self):
        if not self.user_setting_path.exists():
            self.user_setting_path.parent.mkdir(parents=True, exist_ok=True)
            self.user_setting_path.touch()
            with open(self.user_setting_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    @property
    def default_font(self) -> QFont:
        return QFont(self.get("FONT_FAMILY"), self.get("FONT_SIZE"))

    def get(self, key, default=None) -> Any:
        if key in self.user:
            return self.user[key]
        else:
            return self.default.get(key, default)

    def set(self, key, value):
        self.user[key] = value
        with open(self.user_setting_path, "w", encoding="utf-8") as f:
            json.dump(self.user, f, ensure_ascii=False, indent=4)


setting = Setting()
