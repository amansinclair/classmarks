import os
import gc

from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import (
    QMainWindow,
    QGridLayout,
    QWidget,
    QFileDialog,
)

from classmarks import Subject
from .resources import Resources
from .models import StudentModel, TestModel, MarksModel, Sorter
from .menuframe import MenuFrame
from .views import StudentListView, TestListView, MarksTableView
from .dialogs import CatDialog, CheckPasswordDialog, SetPasswordDialog
from .encrypt import Encryptor, PasswordError
from .validators import Validator


class MainWindow(QMainWindow):
    def __init__(self, app, app_path, filepath=None):
        super().__init__()
        self.app = app
        self.app_path = app_path
        self.resources = Resources(app_path)
        self.reset()
        self.set_window()
        self.create_layout()
        self.create_models()
        self.create_widgets()
        self.connect_methods()
        if self.filepath:
            self.load_subject(filepath)

    def reset(self):
        self.subject = Subject()
        self.last_dir = self.app_path
        self.encryptor = None
        self.dirty_project = False
        self.filepath = None
        self.row = None
        self.set_title()

    def refresh(self):
        self.students.update_validator(Validator(self.subject.val_student_name))
        self.tests.update_validator(Validator(self.subject.val_test_name))
        self.sorter.refresh(self.subject)
        self.studentmodel.refresh(self.subject)
        self.testmodel.refresh(self.subject)
        self.marksmodel.refresh(self.subject)
        self.menu.labels["subject"].setText(self.subject.subject_name)
        self.menu.labels["class"].setText(self.subject.grade)
        self.students.clearSelection()

    def load_subject(self, filepath):
        dialog = CheckPasswordDialog(self.resources, self.validate_password, filepath)
        if dialog.exec():
            del dialog
            gc.collect()
            self.last_dir, file = os.path.split(filepath)
            self.dirty_project = False
            self.filepath = filepath
            self.set_title()
            self.refresh()
            self.marksmodel.refresh_size()

    def validate_password(self, path, pw):
        encryptor = Encryptor()
        subject = None
        try:
            subject = encryptor.read(path, pw)
            self.subject = subject
            self.encryptor = encryptor
            del pw
            gc.collect()
        except PasswordError:
            pass
        return subject

    def set_window(self):
        self.setStyleSheet(self.resources.css)
        self.setMinimumSize(800, 400)
        self.app.setWindowIcon(self.resources.icon)
        self.setCursor(self.resources.cursor)

    def set_title(self):
        app_name = "Class Marks"
        if self.filepath:
            app_name = "Class Marks - {}".format(self.filepath)
        self.app.setApplicationName(app_name)
        self.setWindowTitle(app_name)

    def create_layout(self):
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_models(self):
        self.sorter = Sorter(self.subject)
        self.marksmodel = MarksModel(self.subject, self.sorter, self.set_dirty)
        self.studentmodel = StudentModel(
            self.subject, self.marksmodel, self.sorter, self.set_dirty
        )
        self.testmodel = TestModel(self.subject, self.marksmodel, self.set_dirty)

    def create_widgets(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.menu = MenuFrame(self.resources)
        self.layout.addWidget(self.menu, 0, 0)
        self.central.setLayout(self.layout)
        student_val = Validator(self.subject.val_student_name)
        self.students = StudentListView(
            self.studentmodel, self.resources, self.selected_row, student_val,
        )
        self.layout.addWidget(self.students, 1, 0)
        test_val = Validator(self.subject.val_test_name)
        self.tests = TestListView(self.testmodel, self.resources, test_val)
        self.layout.addWidget(self.tests, 0, 1)
        self.marks = MarksTableView(self.marksmodel, self.resources, self.selected_row)
        self.layout.addWidget(self.marks, 1, 1)
        self.vs = self.marks.verticalScrollBar()
        self.vs.setStyleSheet(self.resources.css)
        self.hs = self.marks.horizontalScrollBar()
        self.hs.setStyleSheet(self.resources.css)

    def set_dirty(self):
        self.dirty_project = True

    def open_project(self):
        if self.dirty_project:
            save_it = self.dirty_dialog()
            if save_it != 1:
                self.save_project()
        file, type = QFileDialog.getOpenFileName(
            caption="Open Marks File",
            directory=self.last_dir,
            filter="marks file (*.meow)",
        )
        if file:
            self.load_subject(file)

    def save_project(self):
        warning_showed = False
        if self.encryptor:
            self.encryptor.resave(self.subject)
            self.dirty_project = False
            if not self.subject.check_weights():
                warning_showed = True
                msg = "Warning: Some assessment weights do not sum to 1."
                dia = CatDialog(msg, self.resources, cat_name="cat_tied")
                dia.exec()
        else:
            self.encryptor = Encryptor()
            file, type = QFileDialog.getSaveFileName(
                caption="Save File as",
                directory=self.last_dir,
                filter="marks file (*.meow)",
            )
            if file:
                if "meow" not in file:
                    file += ".meow"
                dialog = SetPasswordDialog(self.resources)
                if dialog.exec():
                    self.encryptor.save(self.subject, dialog.pw, file)
                    self.dirty_project = False
                    self.filepath = file
                    self.last_dir, temp = os.path.split(file)
                    self.set_title()
                    del dialog
                    gc.collect()
        return warning_showed

    def export_project(self):
        if self.subject:
            file, type = QFileDialog.getSaveFileName(
                caption="Export Data as .csv",
                directory=self.last_dir,
                filter="csv file (*.csv)",
            )
            if file:
                self.subject.export(file)

    def new_project(self):
        if self.dirty_project:
            save_it = self.dirty_dialog()
            if save_it != 1:
                self.save_project()
        self.reset()
        self.refresh()

    def add_student(self, event):
        n_students = self.studentmodel.rowCount()
        self.studentmodel.insertRows(n_students)

    def sort_by_gender(self):
        self.sorter.sort_by_gender()
        self.studentmodel.refresh(self.subject)
        self.marksmodel.refresh(self.subject)

    def sort_by_surname(self):
        self.sorter.sort_by_surname()
        self.studentmodel.refresh(self.subject)
        self.marksmodel.refresh(self.subject)

    def sort_by_mark(self):
        self.sorter.sort_by_mark()
        self.studentmodel.refresh(self.subject)
        self.marksmodel.refresh(self.subject)

    def set_subject_name(self):
        self.subject.subject_name = self.menu.labels["subject"].text()

    def set_subject_class(self):
        self.subject.grade = self.menu.labels["class"].text()

    def connect_methods(self):
        self.menu.labels["subject"].textChanged.connect(self.set_subject_name)
        self.menu.labels["class"].textChanged.connect(self.set_subject_class)
        self.menu.menu_buttons["new"].clicked.connect(self.new_project)
        self.menu.menu_buttons["open"].clicked.connect(self.open_project)
        self.menu.menu_buttons["save"].clicked.connect(self.save_project)
        self.menu.menu_buttons["export"].clicked.connect(self.export_project)
        self.menu.student_buttons["add"].clicked.connect(self.add_student)
        self.menu.student_buttons["gender"].clicked.connect(self.sort_by_gender)
        self.menu.student_buttons["name"].clicked.connect(self.sort_by_surname)
        self.menu.student_buttons["mark"].clicked.connect(self.sort_by_mark)
        self.vs.valueChanged.connect(self.scroll_v)
        self.hs.valueChanged.connect(self.scroll_h)

    def scroll_h(self, x):
        self.tests.horizontalScrollBar().setValue(x)
        print(self.hs.maximum())

    def scroll_v(self, y):
        self.students.verticalScrollBar().setValue(y)

    def dirty_dialog(self):
        msg = "You have unsaved data. Would you like to save it?"
        btns = ["Save", "Don't Save"]
        dia = CatDialog(msg, self.resources, buttons=btns, cat_name="cat_tied")
        return dia.exec()

    def selected_row(self, row=None, refresh_students=False, new_index=None, clear=None):
        if clear is not None:
            self.row = None
            self.students.clearSelection()
            self.marksmodel.refresh(self.subject)
        if row is not None:
            self.row = row
            self.marksmodel.refresh(self.subject)
            index = self.studentmodel.index(row, 0)
        if refresh_students:
            self.students.clearSelection()
            self.students.selectionModel().select(
                index, QItemSelectionModel.SelectCurrent
            )
            self.studentmodel.refresh(self.subject)
        if new_index is not None:
            self.marks.setCurrentIndex(new_index)
            self.marks.edit(new_index)
        return self.row

    def closeEvent(self, event):
        if self.dirty_project:
            save_it = self.dirty_dialog()
            if save_it != 1:
                warning = self.save_project()
                if warning:
                    event.ignore()
