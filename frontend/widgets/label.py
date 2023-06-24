from qfluentwidgets import FluentLabelBase, getFont

from setting.setting_reader import setting


class Label(FluentLabelBase):
    def getFont(self):
        return getFont(fontSize=setting.get("FONT_SIZE"))
