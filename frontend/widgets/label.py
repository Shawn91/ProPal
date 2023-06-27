from qfluentwidgets import FluentLabelBase

from setting.setting_reader import setting


class Label(FluentLabelBase):
    def getFont(self):
        return setting.default_font
