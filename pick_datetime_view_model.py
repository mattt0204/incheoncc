from PySide6.QtCore import QObject

from pick_datetime_model import PickDateModel, PickTimeRange, TimeRangeEndpoint


class PickDatetimeViewModel(QObject):
    def __init__(self, scraper):
        self.scraper = scraper
        self.dates_model = PickDateModel()
        self.time_range_model = PickTimeRange(
            start=TimeRangeEndpoint(hour=7, minute=0),
            end=TimeRangeEndpoint(hour=9, minute=0),
        )
        self.load_dates()

    def load_dates(self):
        # 가능한 날짜 선택하게 하기
        self.dates_model.set_dates()
