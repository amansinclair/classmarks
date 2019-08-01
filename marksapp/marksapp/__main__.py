import sys
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QApplication
from .mainwindow import MainWindow


def main():
    filepath = None
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    app_path = QDir().currentPath()
    app = QApplication(sys.argv)
    mainwindow = MainWindow(app, app_path, filepath)
    screen = app.desktop().screenGeometry()
    x = (screen.width() - mainwindow.width()) / 2
    y = (screen.height() - mainwindow.height()) / 2
    mainwindow.move(x, y)
    mainwindow.show()
    app.exec_()


if __name__ == "__main__":
    main()
