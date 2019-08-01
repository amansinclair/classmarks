import os
import json
from PyQt5.QtGui import QColor, QIcon, QPixmap, QCursor


class Resources:
    def __init__(self, app_path):
        self.folder = os.path.join(app_path, "resources")
        with open(os.path.join(self.folder, "colors.json")) as colors:
            self.colors = json.load(colors)
        self.qcolors = self.get_qcolors()
        with open(os.path.join(self.folder, "styles.css")) as css:
            self.css = css.read()
        self.icon = QIcon(os.path.join(self.folder, "icon.ico"))
        self.menu_icons = self.get_menu_icons()
        self.cats = self.get_cats()
        self.pix = self.get_pix()
        self.cursor = self.get_cursor()

    def get_qcolors(self):
        qcolors = dict()
        for name, color in self.colors.items():
            qcolors[name] = QColor(color)
        return qcolors

    def get_menu_icons(self):
        menu_icons = {}
        names = ["new", "open", "save", "export", "add", "gender", "name", "mark"]
        for name in names:
            file = name + ".png"
            menu_icons[name] = QIcon(os.path.join(self.folder, file))
        return menu_icons

    def get_cats(self):
        cats = {}
        names = [
            "cat_clean",
            "cat_hungry",
            "cat_box",
            "cat_walk",
            "cat_poo",
            "cat_tied",
            "cat_eyes",
            "cat_sleep",
            "cat_ghost",
        ]
        for name in names:
            file = name + ".png"
            cat = QPixmap(os.path.join(self.folder, file))
            cats[name] = cat.scaled(64, 64)
        return cats

    def get_pix(self):
        pix = {}
        names = ["male", "female", "paws", "close"]
        for name in names:
            file = name + ".png"
            img = QPixmap(os.path.join(self.folder, file))
            pix[name] = img.scaled(24, 24)
        return pix

    def get_cursor(self):
        cursor = QPixmap(os.path.join(self.folder, "cursor.png"))
        return QCursor(cursor)


if __name__ == "__main__":
    print(os.getcwd())
    root = "."
    r = Resources(root)
    print(r.colors)
    print(r.qcolors)
    print(r.css)
