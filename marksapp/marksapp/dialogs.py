import sys

from functools import partial
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QApplication,
    QLineEdit,
)


class CatDialog(QDialog):
    def __init__(
        self,
        msg,
        resources,
        buttons=["OK"],
        title="Warning",
        cat_name="cat_poo",
        parent=None,
    ):
        super().__init__()
        self.setWindowIcon(resources.icon)
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowSystemMenuHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        layout = QGridLayout()
        self.setStyleSheet(resources.css)
        pic = resources.cats[cat_name]
        cat = QLabel()
        cat.setStyleSheet(resources.css)
        cat.setPixmap(pic)
        txt = QLabel(msg)
        txt.setObjectName("dialog text")
        txt.setStyleSheet(resources.css)
        alignment = Qt.AlignHCenter | Qt.AlignVCenter
        layout.addWidget(txt, 0, 1, 1, len(buttons) + 2, alignment)
        layout.addWidget(cat, 0, 0, alignment)
        self.buttons = []
        for index, button in enumerate(buttons):
            qbutton = QPushButton(button)
            qbutton.clicked.connect(partial(self.on_click, index))
            layout.addWidget(qbutton, 1, index + 3, Qt.AlignRight)
            self.buttons.append(button)
        self.setLayout(layout)

    def on_click(self, index, event):
        self.done(index)

    def closeEvent(self, event):
        self.done(-1)


class CheckPasswordDialog(QDialog):
    def __init__(self, resources, val_func, filepath, parent=None):
        super().__init__(parent)
        self.val_func = val_func
        self.filepath = filepath
        self.setWindowIcon(resources.icon)
        self.setWindowTitle("Password Required")
        self.setWindowFlags(
            Qt.WindowSystemMenuHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        layout = QGridLayout()
        self.setStyleSheet(resources.css)
        cat = QLabel()
        cat.setStyleSheet(resources.css)
        cat.setPixmap(resources.cats["cat_ghost"])
        self.txt = QLabel("Please enter in password.")
        self.txt.setObjectName("dialog text")
        self.txt.setStyleSheet(resources.css)
        self.pw = QLineEdit()
        self.pw.setObjectName("pw")
        self.pw.setEchoMode(QLineEdit.Password)
        self.pw.setFocus()
        alignment = Qt.AlignHCenter | Qt.AlignVCenter
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        layout.addWidget(self.txt, 0, 1, 1, 4, alignment)
        layout.addWidget(cat, 0, 0, 2, 1, alignment)
        layout.addWidget(self.pw, 1, 1, 1, 4, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.ok_button, 2, 3, Qt.AlignRight)
        layout.addWidget(self.cancel_button, 2, 4, Qt.AlignRight)
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.reject)
        self.setLayout(layout)

    def ok_clicked(self):
        valid = self.val_func(self.filepath, self.pw.text())
        if not valid:
            self.txt.setText("Incorrect Password")
            self.pw.setFocus()
        else:
            self.done(1)


class SetPasswordDialog(QDialog):
    def __init__(self, resources, parent=None):
        super().__init__(parent)
        self.pw = None
        self.setWindowIcon(resources.icon)
        self.setWindowTitle("Password Required")
        self.setWindowFlags(
            Qt.WindowSystemMenuHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        layout = QGridLayout()
        self.setStyleSheet(resources.css)
        cat = QLabel()
        cat.setStyleSheet(resources.css)
        cat.setPixmap(resources.cats["cat_ghost"])
        self.txt = QLabel("Please enter in password twice.")
        self.txt.setObjectName("dialog text")
        self.txt.setStyleSheet(resources.css)
        self.pw_top = QLineEdit()
        self.pw_top.setObjectName("pw_top")
        self.pw_top.setEchoMode(QLineEdit.Password)
        self.pw_top.setFocus()
        self.pw_bot = QLineEdit()
        self.pw_bot.setObjectName("pw_bot")
        self.pw_bot.setEchoMode(QLineEdit.Password)
        alignment = Qt.AlignHCenter | Qt.AlignVCenter
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        layout.addWidget(self.txt, 0, 1, 1, 4, alignment)
        layout.addWidget(cat, 0, 0, 3, 1, alignment)
        layout.addWidget(self.pw_top, 1, 1, 1, 4, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.pw_bot, 2, 1, 1, 4, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.ok_button, 3, 3, Qt.AlignRight)
        layout.addWidget(self.cancel_button, 3, 4, Qt.AlignRight)
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.reject)
        self.setLayout(layout)

    def ok_clicked(self):
        valid = self.validate()
        if valid:
            self.pw = self.pw_top.text()
            self.done(1)
        else:
            self.txt.setText("Please re-enter in password.")
            self.pw_top.setFocus()

    def validate(self):
        cond_1 = bool(self.pw_top.text() != "")
        cond_2 = bool(self.pw_top.text() == self.pw_bot.text())
        return bool(cond_1 and cond_2)


if __name__ == "__main__":
    from resources import Resources

    app_path = QDir().currentPath()
    app = QApplication(sys.argv)
    rc = Resources(app_path)
    # dialog = CatDialog('Are you sure you want to delete this student?', rc, ['Ok'])
    dialog = SetPasswordDialog(rc)
    d = dialog.show()
    print(d)
    app.exec_()
