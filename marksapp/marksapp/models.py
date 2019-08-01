from collections import namedtuple
from operator import attrgetter
from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
)

import numpy as np


class Sorter:
    def __init__(self, subject):
        self.refresh(subject)

    def __len__(self):
        return len(self.subject.students)

    def __getitem__(self, index):
        return self.map[index]

    def reset(self):
        self.state = "original"
        self.map = [x for x in range(len(self))]

    def refresh(self, subject):
        self.subject = subject
        self.reset()

    def add(self):
        self.map.append(len(self) - 1)

    def remove(self):
        if self.state == "original":
            self.reset()
        elif self.state == "gender_boy":
            self.state = "gender_girl"
            self.sort_by_gender()
        elif self.state == "gender_girl":
            self.state = "original"
            self.sort_by_gender()
        elif self.state == "surname_a":
            self.state == "original"
            self.sort_by_surname()
        elif self.state == "surname_z":
            self.state == "surname_a"
            self.sort_by_surname()
        elif self.state == "mark_1":
            self.state == "original"
            self.sort_by_mark()
        elif self.state == "mark_6":
            self.state == "mark_1"
            self.sort_by_mark()

    def sort_by_gender(self):
        if self.state == "gender_boy":
            self.reset()
        else:
            sorted_students = sorted(
                self.subject.students,
                key=attrgetter("gender", "last_name", "first_name"),
            )
            indexes = [
                self.subject.students.index(student) for student in sorted_students
            ]
            if self.state == "gender_girl":
                for i, index in enumerate(indexes):
                    if self.subject.students[index].gender == "male":
                        break
                else:
                    i = 0
                indexes = indexes[i:] + indexes[:i]
                self.state = "gender_boy"
            else:
                self.state = "gender_girl"
            self.map = indexes

    def sort_by_surname(self):
        if self.state == "surname_z":
            self.reset()
        else:
            sorted_students = sorted(
                self.subject.students, key=attrgetter("last_name", "first_name")
            )
            indexes = [
                self.subject.students.index(student) for student in sorted_students
            ]
            if self.state == "surname_a":
                indexes.reverse()
                self.state = "surname_z"
            else:
                self.state = "surname_a"
            self.map = indexes

    def sort_by_mark(self):
        if self.state == "mark_6":
            self.reset()
        else:
            root = self.subject.tests[0]
            marks = [
                self.subject.get_mark(student, root)
                for student in self.subject.students
            ]
            indexes = list(np.argsort(marks))
            if self.state == "mark_1":
                indexes.reverse()
                self.state = "mark_6"
            else:
                self.state = "mark_1"
            self.map = indexes


Student = namedtuple("Student", ["fullname", "gender"])


class StudentModel(QAbstractListModel):
    def __init__(self, subject, marksmodel, map, dirty_func, parent=None):
        super().__init__(parent)
        self.marksmodel = marksmodel
        self.set_dirty = dirty_func
        self.map = map
        self.refresh(subject)

    def refresh(self, subject):
        self.subject = subject
        start = self.createIndex(0, 0)
        end = self.createIndex(self.rowCount(), 0)
        self.dataChanged.emit(start, end)

    def rowCount(self, index=QModelIndex()):
        return self.subject.n_students

    def data(self, index, role=Qt.DisplayRole):
        info = QVariant()
        if index.isValid() and role == Qt.DisplayRole:
            mindex = self.map[index.row()]
            student = self.subject.students[mindex]
            info = QVariant(Student(student.fullname, student.gender))
        return info

    def flags(self, index=QModelIndex()):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            mindex = self.map[index.row()]
            student = self.subject.students[mindex]
            self.subject.edit_student(student, **value)
            self.dataChanged.emit(index, index)
            self.set_dirty()
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + 1)
        self.subject.add_student()
        self.map.add()
        self.endInsertRows()
        self.marksmodel.insertRows(position)
        self.set_dirty()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        mindex = self.map[position]
        self.beginRemoveRows(QModelIndex(), mindex, mindex)
        student = self.subject.students[mindex]
        self.subject.delete_student(student)
        self.endRemoveRows()
        self.marksmodel.removeRows(mindex)
        self.set_dirty()
        self.map.remove()
        return True


Test = namedtuple("Test", ["name", "group", "weight", "date"])


class TestModel(QAbstractListModel):
    def __init__(self, subject, marksmodel, dirty_func, parent=None):
        super().__init__(parent)
        self.marksmodel = marksmodel
        self.set_dirty = dirty_func
        self.refresh(subject)

    def refresh(self, subject):
        self.subject = subject
        start = self.createIndex(0, 0)
        end = self.createIndex(self.rowCount(), 0)
        self.dataChanged.emit(start, end)

    def conv_num(self, num):
        text = str(num)
        return text.replace(".", ",")

    def conv_str(self, text):
        text = text.replace(",", ".")
        return float(text)

    def rowCount(self, index=QModelIndex()):
        return self.subject.n_tests

    def data(self, index, role=Qt.DisplayRole):
        info = QVariant()
        if index.isValid() and role == Qt.DisplayRole:
            info = self.subject.tests[index.row()]
            weight = 1.0
            if info.group != "root" or info.group != "test":
                weight = self.conv_num(info.weight)
            info = Test(info.name, info.group, weight, info.date)
            info = QVariant(info)
        return info

    def flags(self, index=QModelIndex()):
        return Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            if "weight" in value.keys():
                value["weight"] = self.conv_str(value["weight"])
            test = self.subject.tests[index.row()]
            self.subject.edit_ass(test, **value)
            self.dataChanged.emit(index, index)
            self.set_dirty()
            return True
        return False

    def add_ass(self, index=QModelIndex()):
        parent_index = index.row()
        parent_ass = self.subject.tests[parent_index]
        offset = self.subject.get_ass_next_index(parent_ass) + 1
        position = parent_index + offset
        self.subject.add_ass(parent=parent_ass)
        self.insertRows(position)
        self.marksmodel.insertColumns(position)
        self.set_dirty()

    def del_ass(self, index=QModelIndex()):
        test_index = index.row()
        test = self.subject.tests[test_index]
        positions = self.subject.delete_ass(test)
        positions.reverse()
        for position in positions:
            self.removeRows(position)
            self.marksmodel.removeColumns(position)
        self.set_dirty()

    def insertRows(self, position, columns=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + 1)
        self.endInsertRows()
        return True

    def removeRows(self, position, columns=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + 1)
        self.endRemoveRows()
        return True


class MarksModel(QAbstractTableModel):
    def __init__(self, subject, map, dirty_func, parent=None):
        super().__init__(parent)
        self.map = map
        self.set_dirty = dirty_func
        self.refresh(subject)

    def refresh(self, subject):
        self.subject = subject
        start = self.createIndex(0, 0)
        end = self.createIndex(self.rowCount(), self.columnCount())
        self.dataChanged.emit(start, end)

    def refresh_size(self):
        for row in range(self.rowCount()):
            self.insertRows(row)
        for col in range(self.columnCount()):
            self.insertColumns(col)

    def reset_data(self, subject):
        self.subject = subject

    def conv_num(self, num):
        text = str(float(num))
        return text.replace(".", ",")

    def conv_str(self, text):
        text = text.replace(",", ".")
        return float(text)

    def refresh_row(self, index):
        row = index.row()
        start = self.createIndex(row, 0)
        end = self.createIndex(row, self.columnCount() - 1)
        self.dataChanged.emit(start, end)

    def data(self, index, role=Qt.DisplayRole):
        info = QVariant()
        if index.isValid() and role == Qt.DisplayRole:
            mindex = self.map[index.row()]
            student = self.subject.students[mindex]
            test = self.subject.tests[index.column()]
            mark = self.conv_num(self.subject.get_mark(student, test))
            info = QVariant(mark)
        return info

    def rowCount(self, index=QModelIndex()):
        return self.subject.n_students

    def columnCount(self, index=QModelIndex()):
        return self.subject.n_tests

    def flags(self, index=QModelIndex()):
        flag = Qt.NoItemFlags
        if self.subject.is_editable(index.column()):
            flag = Qt.ItemIsEnabled | Qt.ItemIsEditable
        return flag

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            value = self.conv_str(value)
            mindex = self.map[index.row()]
            student = self.subject.students[mindex]
            test = self.subject.tests[index.column()]
            self.subject.edit_mark(student, test, value)
            self.dataChanged.emit(index, index)
            self.set_dirty()
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), 0, 0)
        self.endRemoveRows()
        return True

    def insertColumns(self, position, columns=1, index=QModelIndex()):
        self.beginInsertColumns(QModelIndex(), 0, 0)
        self.endInsertColumns()
        return True

    def removeColumns(self, position, columns=1, index=QModelIndex()):
        self.beginRemoveColumns(QModelIndex(), 0, 0)
        self.endRemoveColumns()
        return True
