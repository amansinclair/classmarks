from PyQt5.QtWidgets import QTableView, QListView, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QSize


from .delegates import StudentDelegate, TestDelegate, MarksDelegate


class StudentListView(QListView):
    def __init__(self, model, resources, sel_row_func, validator, parent=None):
        super().__init__(parent)
        self.selected = sel_row_func
        self.setModel(model)
        self.delegate = StudentDelegate(resources, sel_row_func, validator)
        self.setItemDelegate(self.delegate)
        self.setStyleSheet(resources.css)
        self._width = 100
        self._height = 50
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(self._width, self._height))
        scrollbar = self.verticalScrollBar()
        scrollbar.setObjectName("student_scroll")
        scrollbar.setStyleSheet(resources.css)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.update_validator(validator)

    def selectionChanged(self, item, old_item):
        selection = item.indexes()
        if selection:
            self.selected(selection[0].row())

    def wheelEvent(self, event):
        event.ignore()

    def update_validator(self, validator):
        self.delegate.validator = validator


class TestListView(QListView):
    def __init__(self, model, resources, validator, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.delegate = TestDelegate(resources, validator)
        self.setItemDelegate(self.delegate)
        self.setFlow(QListView.LeftToRight)
        self.setStyleSheet(resources.css)
        self._width = 50
        self._height = 250
        self.setGridSize(QSize(self._width, self._height))
        scrollbar = self.horizontalScrollBar()
        scrollbar.setObjectName("test_scroll")
        scrollbar.setStyleSheet(resources.css)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def update_validator(self, validator):
        self.delegate.validator = validator

    def wheelEvent(self, event):
        event.ignore()


class MarksTableView(QTableView):
    def __init__(self, model, resources, sel_row_func, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.setItemDelegate(MarksDelegate(resources, sel_row_func))
        self.selected_row = sel_row_func
        self.setStyleSheet(resources.css)
        self.setShowGrid(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        headers = [self.verticalHeader(), self.horizontalHeader()]
        for header in headers:
            header.setDefaultSectionSize(50)
            header.sectionResizeMode(QHeaderView.Fixed)
            header.hide()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            row = self.selected_row()
            if row != self.model().rowCount() - 1:
                self.selected_row(row + 1, True)
        if key == Qt.Key_Up:
            row = self.selected_row()
            if row != 0:
                self.selected_row(row - 1, True)
