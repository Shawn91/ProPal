from pathlib import Path

import tomli


class Setting:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        with open(self.root_path / 'setting/default.toml', 'rb') as f:
            self.default = tomli.load(f)
        with open(self.root_path / 'setting/user.toml', 'rb') as f:
            self.user = tomli.load(f)

    def get(self, key, default=None):
        if key in self.user:
            return self.user[key]
        else:
            return self.default.get(key, default)


setting = Setting()
