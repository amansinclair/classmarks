from PyQt5.QtWidgets import QToolButton, QFrame, QLabel, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt


class MenuButton(QToolButton):
    def __init__(self, parent, icon, name, css):
        super().__init__(parent)
        self.setIcon(icon)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setText(name)
        self.setStyleSheet(css)


class MenuFrame(QFrame):
    def __init__(self, resources, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.resources = resources
        self.setStyleSheet(resources.css)
        self.object_alignment = Qt.AlignHCenter | Qt.AlignVCenter
        self.layout = self.create_layout()
        self.menu_buttons = self.create_buttons(0, ["new", "open", "save", "export"])
        self.labels = self.create_labels()
        self.create_cats()
        self.student_buttons = self.create_buttons(3, ["add", "gender", "name", "mark"])
        self.setLayout(self.layout)

    def create_layout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for col in range(4):
            layout.setColumnMinimumWidth(col, 98)
        return layout

    def create_buttons(self, row, names):
        buttons = {}
        for index, name in enumerate(names):
            icon = self.resources.menu_icons[name]
            button = MenuButton(self.parent, icon, name, self.resources.css)
            self.layout.addWidget(button, row, index, self.object_alignment)
            buttons[name] = button
        return buttons

    def create_labels(self):
        names = ["subject", "class"]
        labels = {}
        col = 0
        for name in names:
            label = QLineEdit(name)
            label.setAlignment(self.object_alignment)
            self.layout.addWidget(label, 1, col, 1, col + 2, self.object_alignment)
            labels[name] = label
            col += 2
        return labels

    def create_cats(self):
        names = ["cat_clean", "cat_hungry", "cat_box", "cat_walk"]
        for index, name in enumerate(names):
            pic = self.resources.cats[name]
            label = QLabel(parent=self)
            label.setStyleSheet(self.resources.css)
            label.setPixmap(pic)
            self.layout.addWidget(label, 2, index, self.object_alignment)
