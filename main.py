from PySide6.QtWidgets import QApplication

from pick_datetime_view import PickDatetimeView
from pick_datetime_view_model import PickDatetimeViewModel
from scraper import IncheonCCScraper

if __name__ == "__main__":
    app = QApplication([])
    scraper = IncheonCCScraper()
    scraper.login()
    # TODO: 추후 주말 예약이 가능한지 확인 후 가이드 메세지 필요(예약한도)

    view_model = PickDatetimeViewModel(scraper)
    view_model.load_dates()
    widget = PickDatetimeView(app, view_model)
    widget.show()
    app.exec()
