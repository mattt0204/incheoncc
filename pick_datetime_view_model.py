from PySide6.QtCore import QObject


class PickDatetimeViewModel(QObject):
    def __init__(self, scraper):
        self.scraper = scraper

        self.load_dates()

    def load_dates(self):
        # 가능한 날짜 선택하게 하기
        pass
