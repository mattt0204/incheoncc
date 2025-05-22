import arrow
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QStyledItemDelegate

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


class DateWithWeekdayDelegate(QStyledItemDelegate):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model

    def displayText(self, value, locale):
        try:
            weekday = arrow.get(value, "YYYYMMDD").format("ddd", locale="ko_kr")
            return f"{value} ({weekday})"
        except Exception:
            return value
