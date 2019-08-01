from PyQt5.QtGui import QValidator


class Validator(QValidator):

    def __init__(self, val_func, parent=None):
        super().__init__(parent)
        self.val_func = val_func
        self.row = None

    def validate(self, text, cursor_pos):
        if self.row is not None:
            if self.val_func(text, self.row):
                state = QValidator.Acceptable
            else:
                state = QValidator.Invalid
        else:
            state = QValidator.Intermediate
        return (state, text, cursor_pos)
