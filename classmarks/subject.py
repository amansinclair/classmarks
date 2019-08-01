from .testtree import TestTree
from .marksheet import MarkSheet


class Student:
    def __init__(self, fullname, gender):
        self.fullname = fullname
        self.gender = gender

    @property
    def first_name(self):
        return self.fullname.split()[:-1]

    @property
    def last_name(self):
        return self.fullname.split()[-1]

    def __repr__(self):
        return "Student({}, {})".format(self.fullname, self.gender)


class Subject:
    def __init__(self, grade="class", subject_name="subject"):
        self.grade = grade
        self.subject_name = subject_name
        self.student_suffix = 1
        self.cls = self.__class__.__name__
        self.new()

    def __repr__(self):
        msg = "{}(Grade={}, Subject Name={}, Number of Students={})"
        return msg.format(self.cls, self.grade, self.subject_name, self.n_students)

    def new(self):
        self.students = []
        self.marks = MarkSheet()
        self.tests = TestTree()

    def export(self, file_path):
        self.marks.export(file_path)

    def add_student(self, name=None, gender=None):
        if name is None:
            name = "Unnamed {}".format(self.student_suffix)
            self.student_suffix += 1
        if gender is None:
            gender = "male"
        student = Student(name, gender)
        self.students.append(student)
        self.marks.add_student(name)

    def get_student_by_name(self, name):
        for student in self.students:
            if student.fullname == name:
                return student

    def edit_student(self, student, name=None, gender=None):
        if name:
            self.marks.edit_student(student.fullname, name)
            student.fullname = name
        else:
            student.gender = gender

    def delete_student(self, student):
        self.marks.delete_student(student.fullname)
        self.students.remove(student)

    def add_ass(self, name=None, parent=None):
        ass = self.tests.add(name, parent)
        self.marks.add_assessment(ass.name)
        names = [test.name for test in self.tests]
        self.marks.reorder_assessments(names)
        return ass

    def get_ass_next_index(self, parent):
        n_descendants = len(parent.descendants)
        return n_descendants

    def edit_ass(self, ass, **kwargs):
        if "name" in kwargs:
            self.marks.edit_assessment(ass.name, kwargs["name"])
        self.tests.edit(ass, **kwargs)
        if "weight" in kwargs:
            for student in self.students:
                self.propagate_mark(student, ass)

    def delete_ass(self, ass):
        deleted = self.tests.get_family(ass)
        deleted_indexes = [self.tests.get_index(ass) for ass in deleted]
        deleted_asses = self.tests.delete(ass)
        self.marks.delete_assessment(ass.name)
        for ass in deleted_asses:
            self.marks.delete_assessment(ass.name)
        return deleted_indexes

    def get_mark(self, student, ass):
        mark = self.marks.df[ass.name][student.fullname]
        return mark

    def edit_mark(self, student, ass, new_mark):
        self.marks.edit_mark(student.fullname, ass.name, new_mark)
        parent = ass.parent
        parent_mark = self.calc_test_scores(student, parent)
        if parent_mark:
            self.marks.edit_mark(student.fullname, parent.name, parent_mark)
            self.propagate_mark(student, parent)

    def propagate_mark(self, student, ass):
        while ass.parent:
            parent = ass.parent
            marks = []
            new_mark = None
            for child in parent.children:
                mark = self.get_mark(student, child)
                if mark:
                    marks.append(mark * child.weight)
            if len(marks) == len(parent.children):
                new_mark = sum(marks)
            self.marks.edit_mark(student.fullname, parent.name, new_mark)
            ass = parent

    def calc_test_scores(self, student, parent):
        tests = list(parent.children)
        scores = []
        result = None
        for test in tests:
            mark = self.get_mark(student, test)
            if mark:
                scores.append(mark)
        if scores:
            result = sum(scores) / len(scores)
        return result

    def is_editable(self, row):
        group = self.tests[row].group
        return bool(group == "test")

    def check_weights(self):
        value = False
        if self.check_child_weights(self.tests):
            majors = self.tests.children
            value = True
            for major in majors:
                value = self.check_child_weights(major)
                if not value:
                    break
        return value

    def check_child_weights(self, parent):
        value = False
        children = parent.children
        if children:
            children_total = sum([child.weight for child in children])
            if children_total > 0.98 and children_total < 1.02:
                value = True
        else:
            value = True
        return value

    def val_student_name(self, name, row):
        names = [student.fullname for student in self.students]
        names.pop(row)
        return bool(name not in names)

    def val_test_name(self, name, row):
        names = [test.name for test in self.tests]
        names.pop(row)
        return bool(name not in names)

    @property
    def n_students(self):
        return len(self.students)

    @property
    def n_tests(self):
        return len(self.tests)
