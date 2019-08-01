from functools import partial

from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtWidgets import (
    QItemDelegate,
    QLineEdit,
    QStyle,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtGui import QFont, QDoubleValidator, QPen

from .dialogs import CatDialog


class StudentDelegate(QItemDelegate):
    def __init__(self, resources, selected_row, validator, parent=None):
        super().__init__(parent)
        self.resources = resources
        self.selected_row = selected_row
        self.validator = validator
        self.colors = resources.qcolors
        self.male = resources.pix["male"]
        self.female = resources.pix["female"]
        self.close = resources.pix["close"]
        self.font = QFont("Arial", 14)
        self.h = 50
        self.w = 392
        self.y_img = (self.h - self.male.height()) // 2
        self.x_img = (self.w // 8) - (self.male.width() // 2)
        self.x_text = self.w // 4
        self.y_line = self.h - 1

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonPress:
            if self.selected_row() == index.row():
                if event.x() < self.x_text:
                    student = index.data()
                    if student.gender == "male":
                        value = "female"
                    else:
                        value = "male"
                    model.setData(index, {"gender": value})
                if event.x() > self.w - self.x_img:
                    msg = "Are you sure you want to delete this student?"
                    btns = ["Ok", "Cancel"]
                    dia = CatDialog(
                        msg, self.resources, buttons=btns, cat_name="cat_eyes"
                    )
                    keep_it = dia.exec()
                    if not keep_it:
                        model.removeRows(index.row())
                        self.selected_row(clear=True)
        return False

    def paint(self, painter, option, index):
        name = index.data().fullname
        gender = index.data().gender
        pic = self.male
        if gender == "female":
            pic = self.female
        painter.save()
        painter.setFont(self.font)
        text_h = painter.fontMetrics().tightBoundingRect(name).height()
        y_text = ((self.h - text_h) // 2) + text_h
        painter.setPen(self.colors["DARKGREY"])
        if option.state & QStyle.State_Selected:
            painter.setPen(self.colors["LIGHTGREY"])
            painter.fillRect(
                option.rect.x(),
                option.rect.y(),
                option.rect.width(),
                option.rect.height(),
                self.colors["GREEN"],
            )
            painter.drawPixmap(
                self.w - self.x_img, option.rect.y() + self.y_img, self.close
            )
        painter.drawPixmap(
            option.rect.x() + self.x_img, option.rect.y() + self.y_img, pic
        )
        painter.drawText(option.rect.x() + self.x_text, option.rect.y() + y_text, name)
        painter.restore()

    def setModelData(self, editor, model, index):
        model.setData(index, {"name": editor.text()})

    def sizeHint(self, option, index):
        return QSize(self.w, self.h)

    def createEditor(self, parent, option, index):
        line_edit = QLineEdit(parent)
        line_edit.setObjectName("student_edit")
        line_edit.setStyleSheet(self.resources.css)
        line_edit.setFont(self.font)
        self.validator.row = index.row()
        line_edit.setValidator(self.validator)
        return line_edit

    def setEditorData(self, editor, index):
        text = index.data().fullname
        editor.setText(text)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(
            option.rect.x() + self.x_text,
            option.rect.y(),
            self.w - self.x_text - 5,
            self.h - 1,
        )


class TestDelegate(QItemDelegate):
    def __init__(self, resources, validator, parent=None):
        super().__init__(parent)
        self.resources = resources
        self.validator = validator
        self.qcolors = resources.qcolors
        self.colors = {
            "root": self.qcolors["BLUE"],
            "major": self.qcolors["PURPLE"],
            "sub": self.qcolors["GREEN"],
            "test": self.qcolors["MEDIUMGREY"],
        }
        self.sizes = {"root": 250, "major": 230, "sub": 220, "test": 200}
        self.name_font = QFont("Arial", 14)
        self.weight_font = QFont("Arial", 12)
        self.paws = resources.pix["paws"]
        self.h = 250
        self.w = 50
        self.y_img = 10
        self.x_img = (self.w - self.paws.width()) // 2
        self.img_h = self.paws.height()
        self.x_text = self.w // 4

    def paint(self, painter, option, index):
        name = index.data().name
        group = index.data().group
        color = self.colors[group]
        size = self.sizes[group]
        painter.save()
        text_h = painter.fontMetrics().tightBoundingRect(name).height()
        painter.fillRect(
            option.rect.x() + 2, self.h - size, option.rect.width() - 4, size, color
        )
        if group != "test":
            painter.drawPixmap(
                option.rect.x() + self.x_img, self.y_img + (self.h - size), self.paws
            )
        if group != "test" and group != "root":
            painter.setFont(self.weight_font)
            painter.setPen(self.qcolors["DARKGREY"])
            weight = index.data().weight
            w = painter.fontMetrics().tightBoundingRect(weight).width()
            painter.drawText(
                option.rect.x() + ((self.w - w) // 2), self.h - size - 4, weight
            )
        painter.translate(option.rect.x() + 30, self.h - 10)
        painter.rotate(-90)
        painter.setFont(self.name_font)
        painter.setPen(self.qcolors["LIGHTGREY"])
        painter.drawText(0, 0, name)
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(self.w, self.h)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if self.paw_clicked(event, index) and index.data().group != "test":
                model.add_ass(index)
        if event.type() == QEvent.MouseButtonDblClick and index.data().group != "root":
            if not self.paw_clicked(event, index):
                self.validator.row = index.row()
                ass_editor = AssEditor(index.data(), self.resources, self.colors, self.validator)
                resp = ass_editor.exec()
                if resp == 1:
                    self.update_model(ass_editor, model, index)
                if resp == 2:
                    model.del_ass(index)
        return False

    def paw_clicked(self, event, index):
        size = self.sizes[index.data().group]
        rel_loc = event.y() - (self.h - size)
        return bool(rel_loc // (self.img_h + self.y_img) == 0)

    def update_model(self, editor, model, index):
        group = index.data().group
        results = {}
        results["name"] = editor.name_edit.text()
        if group != "test":
            results["weight"] = editor.weight_edit.text()
        else:
            results["date"] = editor.weight_edit.text()
        model.setData(index, results)


class AssEditor(QDialog):
    def __init__(self, test, resources, colors, validator, parent=None):
        super().__init__(parent)
        self.test = test
        self.resources = resources
        ss = ".AssEditor{background-color: " + colors[test.group].name() + ";}"
        self.setStyleSheet(ss)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.layout = QGridLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(test.name)
        self.name_edit.setValidator(validator)
        if test.group != "test":
            weight_label = QLabel("Weight:")
            self.weight_edit = QLineEdit(test.weight)
            validator = QDoubleValidator(0.0, 1.0, 3)
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.weight_edit.setValidator(validator)
        else:
            weight_label = QLabel("Date:")
            self.weight_edit = QLineEdit(str(test.date))
        self.del_button = QPushButton("Delete")
        self.del_button.setStyleSheet(resources.css)
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(resources.css)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(resources.css)
        self.layout.addWidget(name_label, 0, 0)
        self.layout.addWidget(weight_label, 1, 0)
        self.layout.addWidget(self.name_edit, 0, 1, 1, 2)
        self.layout.addWidget(self.weight_edit, 1, 1, 1, 2)
        self.layout.addWidget(self.del_button, 2, 0)
        self.layout.addWidget(self.ok_button, 2, 1)
        self.layout.addWidget(self.cancel_button, 2, 2)
        self.del_button.clicked.connect(self.del_clicked)
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.setLayout(self.layout)
        self.ok_button.setFocus()
        self.ok_button.setAutoDefault(True)
        self.cancel_button.setAutoDefault(False)
        self.del_button.setAutoDefault(False)

    def ok_clicked(self):
        if self.is_validated():
            name_check = bool(self.name_edit.text() != self.test.name)
            weight_check = bool(self.weight_edit.text() != self.test.weight)
            if name_check or weight_check:
                self.done(1)
            else:
                self.done(0)
        else:
            self.weight_edit.setFocus()
            self.weight_edit.selectAll()

    def cancel_clicked(self):
        self.done(0)

    def del_clicked(self):
        msg = "Are you sure you want to delete this Assessment?"
        btns = ["Ok", "Cancel"]
        dia = CatDialog(msg, self.resources, buttons=btns, cat_name="cat_eyes")
        keep_it = dia.exec()
        if not keep_it:
            self.done(2)
            # model.removeRows(index.row())

    def is_validated(self):
        result = True
        if self.test.group != "test":
            weight = int(self.weight_edit.text()[0])
            if weight > 1:
                result = False
            else:
                result = True
        return bool(result)


class MarksDelegate(QItemDelegate):
    def __init__(self, resources, selected_row, parent=None):
        super().__init__(parent)
        self.resources = resources
        self.selected_row = selected_row
        self.colors = resources.qcolors
        self.font = QFont("Arial", 14)
        self.h = 50
        self.w = 50

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonPress:
            if self.selected_row() != index.row():
                self.selected_row(index.row(), True)
        return False

    def paint(self, painter, option, index):
        value = self.format_number(index.data())
        painter.save()
        painter.setFont(self.font)
        text_h = painter.fontMetrics().tightBoundingRect(value).height()
        text_w = painter.fontMetrics().tightBoundingRect(value).width()
        y_text = ((self.h - text_h) // 2) + text_h
        x_text = (self.w - text_w) // 2
        if index.flags() != Qt.NoItemFlags:
            painter.setPen(self.colors["DARKGREY"])
        else:
            painter.setPen(self.colors["MEDIUMGREY"])
        painter.fillRect(
            option.rect.x(),
            option.rect.y() + 1,
            option.rect.width(),
            option.rect.height() - 2,
            self.colors["WHITE"],
        )
        painter.drawText(option.rect.x() + x_text, option.rect.y() + y_text, value)
        if index.row() == self.selected_row():
            painter.setPen(QPen(self.colors["GREEN"], 3))
            if index.column() == index.model().columnCount() - 1:
                painter.drawLine(
                    option.rect.x() + self.w,
                    option.rect.y() + 1,
                    option.rect.x() + self.w,
                    option.rect.y() + self.h - 2,
                )
            painter.drawLine(
                option.rect.x(),
                option.rect.y() + 1,
                option.rect.x() + self.w,
                option.rect.y() + 1,
            )
            painter.drawLine(
                option.rect.x(),
                option.rect.y() + self.h - 2,
                option.rect.x() + self.w,
                option.rect.y() + self.h - 2,
            )
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(self.w, self.h)

    def createEditor(self, parent, option, index):
        line_edit = QLineEdit(parent)
        line_edit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        line_edit.setObjectName("marks_edit")
        line_edit.setStyleSheet(self.resources.css)
        line_edit.setFont(self.font)
        validator = QDoubleValidator(1.0, 6.0, 1)
        validator.setNotation(QDoubleValidator.StandardNotation)
        line_edit.setValidator(validator)
        line_edit.returnPressed.connect(partial(self.update_model, index, line_edit))
        return line_edit

    def setEditorData(self, editor, index):
        text = index.data()
        editor.setText(text)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(
            option.rect.x() + 3,
            option.rect.y() + 3,
            option.rect.width() - 6,
            option.rect.height() - 6,
        )

    def format_number(self, text):
        if text == "nan":
            text = "0,0"
        if len(text) > 2:
            num = float(text.replace(",", "."))
            num = round(num, 2)
            text = str(num).replace(".", ",")
        return text

    def update_model(self, index, line_edit):
        model = index.model()
        model.setData(index, line_edit.text())
        n_rows = model.rowCount()
        if self.selected_row() < n_rows - 1:
            new_index = model.index(index.row() + 1, index.column())
            self.selected_row(index.row() + 1, True, new_index)
