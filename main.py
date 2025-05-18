from PySide6.QtWidgets import QApplication

from pick_datetime_view import PickDatetimeView
from pick_datetime_view_model import PickDatetimeViewModel
from scraper import IncheonCCScraper


def main():
    print("Hello, World!")


if __name__ == "__main__":
    app = QApplication([])
    scraper = IncheonCCScraper()
    view_model = PickDatetimeViewModel(scraper)
    widget = PickDatetimeView(app, view_model)
    widget.show()
    app.exec()
