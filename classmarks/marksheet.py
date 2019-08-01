import pandas as pd


class MarkSheet:
    def __init__(self):
        self.df = pd.DataFrame()
        self.df.index.name = "Students"
        self.df["Total"] = 0

    def __repr__(self):
        return "MarkSheet(rows={}, columns={})".format(*self.df.shape)

    def __str__(self):
        return str(self.df)

    def add_student(self, name):
        self.df.loc[name] = 0

    def delete_student(self, name):
        self.df.drop(name, axis=0, inplace=True)

    def edit_student(self, name, new_name):
        self.df.rename(index={name: new_name}, inplace=True)

    def add_assessment(self, assessment):
        self.df[assessment] = 0

    def delete_assessment(self, assessment):
        self.df.drop(assessment, axis=1, inplace=True)

    def edit_assessment(self, assessment, new_assessment):
        self.df.rename(columns={assessment: new_assessment}, inplace=True)

    def edit_mark(self, name, assessment, mark):
        self.df.loc[name, assessment] = mark

    def reorder_assessments(self, names):
        self.df = self.df[names]

    def reorder_students(self, names):
        self.df = self.df.loc[names]

    def export(self, file_path):
        self.df.to_csv(file_path, sep=";")
