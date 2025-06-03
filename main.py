from PySide6.QtWidgets import QApplication

from pick_datetime_view import PickDatetimeView
from pick_datetime_view_model import PickDatetimeViewModel

if __name__ == "__main__":
    app = QApplication([])
    view_model = PickDatetimeViewModel()
    view_model.load_dates()
    widget = PickDatetimeView(app, view_model)
    widget.show()
    app.exec()
