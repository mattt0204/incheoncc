from PySide6.QtWidgets import QWidget


class PickDatetimeView(QWidget):
    def __init__(self, app, view_model):
        self.app = app
        self.view_model = view_model
