from pathlib import Path
from typing import Any

import tomli
from PySide6.QtGui import QFont


class Setting:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        with open(self.root_path / "setting/default.toml", "rb") as f:
            self.default = tomli.load(f)
        with open(self.root_path / "setting/user.toml", "rb") as f:
            self.user = tomli.load(f)

    @property
    def default_font(self) -> QFont:
        return QFont(self.get("FONT_FAMILY"), self.get("FONT_SIZE"))

    def get(self, key, default=None) -> Any:
        if key in self.user:
            return self.user[key]
        else:
            return self.default.get(key, default)


setting = Setting()
